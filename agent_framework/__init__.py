class ChatAgent:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass
    async def run(self, *args, **kwargs):
        class Result:
            content = "mock answer"
            citations = []
            sources_used = []
            confidence_score = 0.9
        return Result()
