import os
import requests
import json
import logging
from typing import Dict, Any, Optional, List
import time

class LLMClient:
    """LLM客户端，用于调用GLM API"""

    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key or os.getenv('GLM_API_KEY')
        self.api_base = api_base or "https://open.bigmodel.cn/api/paas/v4"
        self.logger = logging.getLogger(__name__)

        if not self.api_key:
            raise ValueError("GLM API key is required")

        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.logger.info("LLM客户端初始化完成")

    def generate_response(self,
                         prompt: str,
                         context: str = "",
                         max_tokens: int = 1024,
                         temperature: float = 0.7,
                         system_prompt: str = None) -> str:
        """
        生成回答

        Args:
            prompt: 用户提示
            context: 上下文信息（知识库检索结果）
            max_tokens: 最大生成长度
            temperature: 温度参数
            system_prompt: 系统提示词

        Returns:
            生成的回答
        """
        try:
            # 构建完整的提示
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n上下文信息:\n{context}\n\n用户问题: {prompt}"
            else:
                full_prompt = f"上下文信息:\n{context}\n\n用户问题: {prompt}"

            # 准备请求数据
            data = {
                "model": "glm-4v-flash",  # 使用GLM-4V Flash模型
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }

            # 发送请求
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )

            # 检查响应
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    answer = result['choices'][0]['message']['content']
                    self.logger.info("生成回答成功")
                    return answer.strip()
                else:
                    raise ValueError("API返回格式错误")
            else:
                error_msg = response.text
                raise Exception(f"API请求失败: {response.status_code} - {error_msg}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            raise Exception(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析失败: {e}")
            raise Exception(f"响应解析失败: {e}")
        except Exception as e:
            self.logger.error(f"生成回答失败: {e}")
            raise

    def batch_generate(self,
                      prompts: List[str],
                      contexts: List[str] = None,
                      max_tokens: int = 1024,
                      temperature: float = 0.7) -> List[str]:
        """
        批量生成回答

        Args:
            prompts: 提示列表
            contexts: 上下文列表（可选）
            max_tokens: 最大生成长度
            temperature: 温度参数

        Returns:
            回答列表
        """
        answers = []

        if contexts is None:
            contexts = [""] * len(prompts)

        for i, (prompt, context) in enumerate(zip(prompts, contexts)):
            try:
                answer = self.generate_response(
                    prompt=prompt,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                answers.append(answer)

                # 避免API限流
                if i < len(prompts) - 1:
                    time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"第{i+1}个回答生成失败: {e}")
                answers.append(f"生成失败: {str(e)}")

        return answers

    def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_prompt = "请回复'连接成功'"
            response = self.generate_response(
                prompt=test_prompt,
                max_tokens=10,
                temperature=0.1
            )
            return "连接成功" in response
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False