from dragonk8s.lib.util.timeutil.rate import Limiter
import time


class PassiveRateLimiter(object):

    def try_accept(self) -> bool:
        pass

    def stop(self):
        pass

    def qps(self) -> float:
        pass


class RateLimiter(PassiveRateLimiter):

    def accept(self):
        pass

    def wait(self, timeout=0):
        pass


class TokenBucketPassiveRateLimiter(RateLimiter):

    def __init__(self, limiter: Limiter, qps: float):
        super().__init__()
        self._limiter = limiter
        self._qps = qps


class TokenBucketRateLimiter(TokenBucketPassiveRateLimiter):

    def __init__(self, qps: float, burst: int = 0, limiter: Limiter = None):
        if limiter is None:
            limiter = Limiter(qps, burst)
        super(TokenBucketRateLimiter, self).__init__(limiter, qps)

    def try_accept(self) -> bool:
        return self._limiter.allow_n(time.time(), 1)

    def stop(self):
        pass

    def qps(self) -> float:
        return self._qps

    def accept(self):
        now = time.time()
        time.sleep(self._limiter.reverve_n(now, 1).delay_from(now))

    def wait(self, timeout=0):
        return self._limiter.wait(timeout)