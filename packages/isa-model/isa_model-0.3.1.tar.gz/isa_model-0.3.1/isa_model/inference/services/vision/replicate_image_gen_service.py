#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Replicate 图像生成服务
支持 flux-schnell (文生图) 和 flux-kontext-pro (图生图) 模型
"""

import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Union
import asyncio
import aiohttp
import replicate
from PIL import Image
from io import BytesIO

from isa_model.inference.services.vision.base_image_gen_service import BaseImageGenService
from isa_model.inference.providers.base_provider import BaseProvider

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplicateImageGenService(BaseImageGenService):
    """
    Replicate 图像生成服务
    - flux-schnell: 文生图 (t2i) - $3 per 1000 images
    - flux-kontext-pro: 图生图 (i2i) - $0.04 per image
    """
    
    def __init__(self, provider: BaseProvider, model_name: str):
        super().__init__(provider, model_name)
        
        # 获取配置
        provider_config = provider.get_full_config()
        self.api_token = provider_config.get("api_token") or provider_config.get("replicate_api_token")
        
        if not self.api_token:
            raise ValueError("Replicate API token not found in provider configuration")
        
        # 设置 API token
        os.environ["REPLICATE_API_TOKEN"] = self.api_token
        
        # 生成图像存储目录
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 统计信息
        self.last_generation_count = 0
        self.total_generation_count = 0
        
        logger.info(f"Initialized ReplicateImageGenService with model '{self.model_name}'")

    async def generate_image(
        self, 
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """生成单张图像 (文生图)"""
        
        if "flux-schnell" in self.model_name:
            # FLUX Schnell 参数
            input_data = {
                "prompt": prompt,
                "go_fast": True,
                "megapixels": "1",
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg",
                "output_quality": 90,
                "num_inference_steps": 4
            }
        else:
            # 默认参数
            input_data = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale
            }
            
            if negative_prompt:
                input_data["negative_prompt"] = negative_prompt
            if seed:
                input_data["seed"] = seed
        
        return await self._generate_internal(input_data)

    async def image_to_image(
        self,
        prompt: str,
        init_image: Union[str, Any],
        strength: float = 0.8,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """图生图"""
        
        if "flux-kontext-pro" in self.model_name:
            # FLUX Kontext Pro 参数
            input_data = {
                "prompt": prompt,
                "input_image": init_image,
                "aspect_ratio": "match_input_image",
                "output_format": "jpg",
                "safety_tolerance": 2
            }
        else:
            # 默认参数
            input_data = {
                "prompt": prompt,
                "image": init_image,
                "strength": strength,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale
            }
            
            if negative_prompt:
                input_data["negative_prompt"] = negative_prompt
            if seed:
                input_data["seed"] = seed
        
        return await self._generate_internal(input_data)

    async def _generate_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """内部生成方法"""
        try:
            logger.info(f"开始使用模型 {self.model_name} 生成图像")
            
            # 调用 Replicate API
            output = await replicate.async_run(self.model_name, input=input_data)
            
            # 处理输出
            if isinstance(output, list):
                urls = output
            else:
                urls = [output]

            # 更新统计
            self.last_generation_count = len(urls)
            self.total_generation_count += len(urls)
            
            # 计算成本
            cost = self._calculate_cost(len(urls))
            
            # 跟踪计费信息
            from isa_model.inference.billing_tracker import ServiceType
            self._track_usage(
                service_type=ServiceType.IMAGE_GENERATION,
                operation="image_generation",
                input_units=len(urls),  # 生成的图像数量
                metadata={
                    "model": self.model_name,
                    "prompt": input_data.get("prompt", "")[:100],  # 截取前100字符
                    "generation_type": "t2i" if "flux-schnell" in self.model_name else "i2i"
                }
            )
            
            result = {
                "urls": urls,
                "count": len(urls),
                "cost_usd": cost,
                "model": self.model_name,
                "metadata": {
                    "input": input_data,
                    "generation_count": len(urls)
                }
            }
            
            logger.info(f"图像生成完成: {len(urls)} 张图像, 成本: ${cost:.6f}")
            return result
            
        except Exception as e:
            logger.error(f"图像生成失败: {e}")
            raise

    def _calculate_cost(self, image_count: int) -> float:
        """计算生成成本"""
        from isa_model.core.model_manager import ModelManager
        
        manager = ModelManager()
        
        if "flux-schnell" in self.model_name:
            # $3 per 1000 images
            return (image_count / 1000) * 3.0
        elif "flux-kontext-pro" in self.model_name:
            # $0.04 per image
            return image_count * 0.04
        else:
            # 使用 ModelManager 的定价
            pricing = manager.get_model_pricing("replicate", self.model_name)
            return (image_count / 1000) * pricing.get("input", 0.0)

    async def generate_images(
        self, 
        prompt: str,
        num_images: int = 1,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """生成多张图像"""
        results = []
        for i in range(num_images):
            current_seed = seed + i if seed else None
            result = await self.generate_image(
                prompt, negative_prompt, width, height, 
                num_inference_steps, guidance_scale, current_seed
            )
            results.append(result)
        return results

    async def generate_image_to_file(
        self, 
        prompt: str,
        output_path: str,
        negative_prompt: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 4,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """生成图像并保存到文件"""
        result = await self.generate_image(
            prompt, negative_prompt, width, height, 
            num_inference_steps, guidance_scale, seed
        )
        
        # 保存第一张图像
        if result.get("urls"):
            url = result["urls"][0]
            url_str = str(url) if hasattr(url, "__str__") else url
            await self._download_image(url_str, output_path)
            
            return {
                "file_path": output_path,
                "cost_usd": result.get("cost_usd", 0.0),
                "model": self.model_name
            }
        else:
            raise ValueError("No image generated")

    async def _download_image(self, url: str, save_path: str) -> None:
        """下载图像并保存"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    with Image.open(BytesIO(content)) as img:
                        img.save(save_path)
        except Exception as e:
            logger.error(f"下载图像时出错: {url}, {e}")
            raise

    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        total_cost = 0.0
        if "flux-schnell" in self.model_name:
            total_cost = (self.total_generation_count / 1000) * 3.0
        elif "flux-kontext-pro" in self.model_name:
            total_cost = self.total_generation_count * 0.04
        
        return {
            "last_generation_count": self.last_generation_count,
            "total_generation_count": self.total_generation_count,
            "total_cost_usd": total_cost,
            "model": self.model_name
        }

    def get_supported_sizes(self) -> List[Dict[str, int]]:
        """获取支持的图像尺寸"""
        if "flux" in self.model_name:
            return [
                {"width": 512, "height": 512},
                {"width": 768, "height": 768},
                {"width": 1024, "height": 1024},
            ]
        else:
            return [
                {"width": 512, "height": 512},
                {"width": 768, "height": 768},
                {"width": 1024, "height": 1024},
                {"width": 768, "height": 1344},
                {"width": 1344, "height": 768},
            ]

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if "flux-schnell" in self.model_name:
            return {
                "name": self.model_name,
                "type": "t2i",
                "cost_per_1000_images": 3.0,
                "supports_negative_prompt": False,
                "supports_img2img": False,
                "max_steps": 4
            }
        elif "flux-kontext-pro" in self.model_name:
            return {
                "name": self.model_name,
                "type": "i2i",
                "cost_per_image": 0.04,
                "supports_negative_prompt": False,
                "supports_img2img": True,
                "max_width": 1024,
                "max_height": 1024
            }
        else:
            return {
                "name": self.model_name,
                "type": "general",
                "supports_negative_prompt": True,
                "supports_img2img": True
            }

    async def load(self) -> None:
        """加载服务"""
        if not self.api_token:
            raise ValueError("缺少 Replicate API 令牌")
        logger.info(f"Replicate 图像生成服务已准备就绪，使用模型: {self.model_name}")

    async def unload(self) -> None:
        """卸载服务"""
        logger.info(f"卸载 Replicate 图像生成服务: {self.model_name}")

    async def close(self):
        """关闭服务"""
        await self.unload()

