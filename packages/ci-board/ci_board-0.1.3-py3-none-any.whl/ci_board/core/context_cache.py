# 杂鱼♡～本喵设计的通用上下文缓存系统喵～
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

from ci_board.utils import get_component_logger

T = TypeVar("T")


class ContextCache(Generic[T]):
    """杂鱼♡～通用的上下文缓存系统，带有时间窗口和内容哈希喵～"""

    def __init__(
        self,
        cache_max_size: int = 10,
        dedup_window: float = 1.0,
        cache_name: str = "cache",
    ):
        """
        杂鱼♡～初始化上下文缓存喵～
        
        Args:
            cache_max_size: 缓存最大条目数
            dedup_window: 去重时间窗口（秒）
            cache_name: 缓存名称，用于日志
        """
        self.logger = get_component_logger(f"core.context_cache.{cache_name}")
        self._last_content_hash: str = ""
        self._content_cache: Dict[str, float] = {}
        self._cache_max_size = cache_max_size
        self._dedup_window = dedup_window
        self._cache_name = cache_name

    def is_duplicate(self, content: T, hash_calculator: callable) -> bool:
        """
        杂鱼♡～检查内容是否重复喵～
        
        Args:
            content: 要检查的内容
            hash_calculator: 哈希计算函数，接收内容并返回哈希字符串
            
        Returns:
            True 如果是重复内容，False 如果不是
        """
        try:
            content_hash = hash_calculator(content)
        except Exception as e:
            self.logger.error(f"杂鱼♡～计算内容哈希失败喵：{e}")
            return False  # 杂鱼♡～计算失败就不当作重复处理喵～

        # 杂鱼♡～检查是否与上一个内容完全相同喵～
        if content_hash == self._last_content_hash:
            self.logger.debug("内容哈希与上一个完全相同，跳过。")
            return True

        # 杂鱼♡～检查是否在时间窗口内有重复喵～
        if content_hash in self._content_cache:
            last_time = self._content_cache[content_hash]
            if time.time() - last_time < self._dedup_window:
                self.logger.debug(f"在 {self._dedup_window}s 的去重窗口内检测到重复内容，跳过。")
                return True

        # 杂鱼♡～更新缓存喵～
        self._last_content_hash = content_hash
        self._content_cache[content_hash] = time.time()
        self._cleanup_cache()
        return False

    def _cleanup_cache(self):
        """杂鱼♡～清理过期的缓存项喵～"""
        if len(self._content_cache) > self._cache_max_size:
            # 杂鱼♡～简单地按插入顺序（在Python 3.7+中）丢掉最旧的项喵～
            num_to_remove = len(self._content_cache) - self._cache_max_size
            for _ in range(num_to_remove):
                # 杂鱼♡～iter 和 next 会获取第一个 (最老的) 键
                oldest_key = next(iter(self._content_cache))
                del self._content_cache[oldest_key]
            self.logger.debug(f"清理了 {num_to_remove} 个缓存项。")

    def clear(self):
        """杂鱼♡～清空缓存喵～"""
        self._content_cache.clear()
        self._last_content_hash = ""
        self.logger.debug("缓存已清空。")

    def get_stats(self) -> Dict[str, Any]:
        """杂鱼♡～获取缓存统计信息喵～"""
        return {
            "cache_name": self._cache_name,
            "cache_size": len(self._content_cache),
            "max_size": self._cache_max_size,
            "dedup_window": self._dedup_window,
            "last_hash": self._last_content_hash[:16] + "..." if self._last_content_hash else "",
        } 