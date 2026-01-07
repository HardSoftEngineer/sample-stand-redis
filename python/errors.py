class InfrastructureUnavailableError(RuntimeError):
    pass

class RedisUnavailableError(InfrastructureUnavailableError):
    pass
