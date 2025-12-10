import logging
from sentence_transformers import SentenceTransformer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalEmbedder:
    def __init__(self):
        logger.info("🧠 Loading Embedding Model (all-MiniLM-L6-v2)...")
        # 这是一个非常轻量级的模型，只有 80MB，跑在 CPU 上也很快
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def generate_embedding(self, text: str) -> list:
        """
        将文本转换为 384 维向量
        """
        if not text:
            return [0.0] * 384
            
        # 生成向量
        embedding = self.model.encode(text)
        # 转换为列表返回
        return embedding.tolist()

# 单例模式，避免重复加载模型
_embedder_instance = None

def get_embedding(text: str):
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = LocalEmbedder()
    return _embedder_instance.generate_embedding(text)

if __name__ == "__main__":
    # 测试代码
    vec = get_embedding("Hello AI World")
    print(f"✅ Generated vector with dimension: {len(vec)}")
    print(f"Sample: {vec[:5]}...")
    