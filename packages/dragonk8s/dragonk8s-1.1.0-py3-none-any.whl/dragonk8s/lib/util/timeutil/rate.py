from threading import Lock
import time


Inf = float("inf")


def every(interval: int) -> float:
    if interval <= 0:
        return Inf
    return 1 / float(interval)


def duration_from_tokens(limit, tokens: float):
    if limit <= 0:
        return Inf
    return float(tokens/limit)


def tokens_from_duration(limit, d):
    if limit <= 0:
        return 0
    return float(d * limit)


class RateLimitException(Exception):
    pass


class Reservation(object):

    def __init__(self, ok=False, lim=None, tokens=0, time_to_act=0, limit=0):
        self._ok = ok
        self._lim = lim
        self._tokens = tokens
        self._time_to_act = time_to_act
        self._limit = limit

    @property
    def ok(self):
        return self._ok

    def delay_from(self, now):
        if not self._ok:
            return Inf
        delay = self._time_to_act - now
        if delay < 0:
            return 0
        return delay

    def delay(self):
        return self.delay_from(time.time())

    def cancel_at(self, now):
        if not self._ok:
            return
        try:
            self._lim.lock.acquire(True)
            if self._lim._limit == Inf or self._tokens == 0 or self._time_to_act < now:
                return
            restore_tokens = self._tokens - duration_from_tokens(self._limit, self._lim.last_event - self._time_to_act)
            if restore_tokens <= 0:
                return
            now, _, tokens = self._lim._advance(now)
            tokens += restore_tokens
            burst = float(self._lim._burst)
            if tokens > burst:
                tokens = burst
            self._lim._last = now
            self._lim.tokens = tokens
            if self._time_to_act == self._lim.last_event:
                prev_event = self._time_to_act + duration_from_tokens(self._limit, float(-1 * self._tokens))
                if not prev_event < now:
                    self._lim.last_event = prev_event
        finally:
            self._lim.lock.release()

    def cancel(self):
        self.cancel_at(time.time())


class Limiter(object):

    # 令牌桶, 每秒limit个, 允许b个突发
    def __init__(self, limit: float, burst: int):
        self.lock = Lock()
        self._limit = limit
        self._burst = burst
        self._tokens = float(0)
        self._last = float(0)
        self.last_event = float(0)

    @property
    def limit(self):
        try:
            self.lock.acquire(True)
            return self._limit
        finally:
            self.lock.release()

    @property
    def burst(self):
        try:
            self.lock.acquire(True)
            return self._burst
        finally:
            self.lock.release()

    # 向前推进
    def _advance(self, now):
        last = self._last
        if now < last:
            last = now
        # 比last过去了的时间
        elapsed = now - last
        # 这些时间应该产生多少令牌
        delta = tokens_from_duration(self._limit, elapsed)
        tokens = self._tokens + delta
        burst = float(self._burst)
        if tokens > burst:
            tokens = burst
        return now, last, tokens

    def _reserve_n(self, now, n: int, max_future_reserve: float) -> Reservation:
        try:
            self.lock.acquire(True)
            if self._limit == Inf:
                return Reservation(ok=True, lim=self, tokens=n, time_to_act=now)
            elif self._limit == 0:
                ok = False
                if self._burst >= n:
                    ok = True
                    self._burst -= n
                return Reservation(ok=ok, lim=self, tokens=self._burst, time_to_act=now)
            now, last, tokens = self._advance(now)
            tokens -= float(n)
            wait_duration = 0
            if tokens < 0:
                wait_duration = duration_from_tokens(self._limit, -1 * tokens)
            ok = n <= self._burst and wait_duration <= max_future_reserve
            r = Reservation(ok=ok, lim=self, limit=self._limit)
            if ok:
                r._tokens = n
                r._time_to_act = now + wait_duration

            if ok:
                self._last = now
                self._tokens = tokens
                self.last_event = r._time_to_act
            else:
                self._last = last
            return r
        finally:
            self.lock.release()

    # 申请n个令牌，返回true申请成功，可以act，返回false，申请失败，不可以act
    def allow_n(self, now, n) -> bool:
        return self._reserve_n(now, n, float(0)).ok

    def allow(self) -> bool:
        return self.allow_n(time.time(), 1)

    # 申请n个令牌, 返回一个Reservation 记为r，如果r.ok == false, 那么不允许act，因为超过了burst
    # 如果r.ok == true， 可以time.sleep(r.delay()) 就可以act，不act的话就得r.cancel()
    def reverve_n(self, now, n) -> Reservation:
        return self._reserve_n(now, n, Inf)

    def reserve(self):
        return self.reverve_n(time.time(), 1)

    # 比reverve_n的不同就是自动sleep了
    def wait_n(self, n, timeout=0):
        self.lock.acquire(True)
        burst = self._burst
        limit = self._limit
        self.lock.release()

        if n > burst and limit != Inf:
            raise RateLimitException("rate: Wait(n=%d) exceeds limiter's burst %d" % (n, burst))

        now = time.time()
        wait_limit = Inf
        if timeout > 0:
            wait_limit = timeout
        r = self._reserve_n(now, n, wait_limit)
        if not r.ok:
            raise RateLimitException("rate: Wait(n=%d) would exceed timeout" % n)

        delay = r.delay_from(now)
        if delay == 0:
            return
        time.sleep(delay)

    def wait(self, timeout=0):
        return self.wait_n(1, timeout=timeout)

    def set_limit_at(self, now, new_limit):
        try:
            self.lock.acquire(True)
            now, _, tokens = self._advance(now)
            self._last = now
            self._tokens = tokens
            self._limit = new_limit
        finally:
            self.lock.release()

    def set_limit(self, new_limit):
        self.set_limit_at(time.time(), new_limit)

    def set_burst_at(self, now, new_burst):
        try:
            self.lock.acquire(True)
            now, _, tokens = self._advance(now)
            self._last = now
            self._tokens = tokens
            self._burst = new_burst
        finally:
            self.lock.release()

    def set_burst(self, new_burst):
        self.set_burst_at(time.time(), new_burst)
