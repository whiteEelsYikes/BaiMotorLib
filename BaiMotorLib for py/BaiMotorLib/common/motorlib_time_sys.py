class MotorlibTimeSys:
    # 时间比较返回常量
    OnceUponATime = 0  # 给定时间 < 当前时间
    NowTheTime = 1  # 给定时间 = 当前时间
    FutureTime = 2  # 给定时间 > 当前时间

    def __init__(self):
        # 初始化时间成员变量，分别存储毫秒、秒、分、时
        self.MS = 0  # 0 ~ 999
        self.SEC = 0  # 0 ~ 59
        self.MIN = 0  # 0 ~ 59
        self.HOUR = 0  # 无上限，持续累加

    def tick_inc(self, ms=0, sec=0, min=0, hour=0):
        """
        时间累加方法，支持多单位同时累加，自动处理进位逻辑
        :param ms: 要累加的毫秒数，非负整数（默认0）
        :param sec: 要累加的秒数，非负整数（默认0）
        :param min: 要累加的分钟数，非负整数（默认0）
        :param hour: 要累加的小时数，非负整数（默认0）
        :raises ValueError: 传入负数时抛出异常
        """
        # 合法性校验：禁止传入负数
        if any(x < 0 for x in [ms, sec, min, hour]):
            raise ValueError("累加的时间值不能为负数（ms/sec/min/hour 均需≥0）")

        # 步骤1：先累加所有单位的原始值，不处理进位
        self.MS += ms
        self.SEC += sec
        self.MIN += min
        self.HOUR += hour

        # 步骤2：处理毫秒进位 → 1000毫秒 = 1秒，取余保留剩余毫秒，商为进位秒数
        if self.MS >= 1000:
            sec_carry = self.MS // 1000  # 计算毫秒向秒的进位值
            self.MS = self.MS % 1000  # 保留0~999的毫秒数
            self.SEC += sec_carry  # 进位累加到秒

        # 步骤3：处理秒进位 → 60秒 = 1分，取余保留剩余秒数，商为进位分数
        if self.SEC >= 60:
            min_carry = self.SEC // 60
            self.SEC = self.SEC % 60
            self.MIN += min_carry

        # 步骤4：处理分进位 → 60分 = 1时，取余保留剩余分数，商为进位数
        if self.MIN >= 60:
            hour_carry = self.MIN // 60
            self.MIN = self.MIN % 60
            self.HOUR += hour_carry

    def compare_time(self, ms, sec, min, hour):
        """
        时间比较方法，按 时→分→秒→毫秒 优先级依次比较
        :param ms: 待比较的毫秒数（非负整数，建议0~999）
        :param sec: 待比较的秒数（非负整数，建议0~59）
        :param min: 待比较的分钟数（非负整数，建议0~59）
        :param hour: 待比较的小时数（非负整数，无上限）
        :raises ValueError: 传入负数时抛出异常
        :return: OnceUponATime(0)/NowTheTime(1)/FutureTime(2)
        """
        # 合法性校验：禁止传入负数
        if any(x < 0 for x in [ms, sec, min, hour]):
            raise ValueError("比较的时间值不能为负数（ms/sec/min/hour 均需≥0）")

        # 按优先级从高到低比较：小时 → 分钟 → 秒 → 毫秒
        if hour > self.HOUR:
            return self.FutureTime
        elif hour < self.HOUR:
            return self.OnceUponATime
        # 小时相等，比较分钟
        elif min > self.MIN:
            return self.FutureTime
        elif min < self.MIN:
            return self.OnceUponATime
        # 分钟相等，比较秒
        elif sec > self.SEC:
            return self.FutureTime
        elif sec < self.SEC:
            return self.OnceUponATime
        # 秒相等，比较毫秒
        elif ms > self.MS:
            return self.FutureTime
        elif ms < self.MS:
            return self.OnceUponATime
        # 所有单位相等
        else:
            return self.NowTheTime

    def get_ms(self):
        """获取当前毫秒值（0~999）"""
        return self.MS

    def get_sec(self):
        """获取当前秒值（0~59）"""
        return self.SEC

    def get_time(self):
        """
        获取当前完整时间，返回元组格式
        :return: tuple (hour, min, sec, ms)，对应时、分、秒、毫秒
        """
        return (self.HOUR, self.MIN, self.SEC, self.MS)