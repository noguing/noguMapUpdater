import sched
import time


# 初始化sched模块的 scheduler 类
# 第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
schedule = sched.scheduler(time.time, time.sleep)


# 被周期性调度触发的函数 启动任务
def go(inc):
    # main()
    print(1)
    schedule.enter(inc, 0, go, (inc,))


# 三天一次
def cycle(inc=86400*3):
    # enter四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，
    # 给该触发函数的参数（tuple形式）
    schedule.enter(0, 0, go, (inc,))
    schedule.run()


if __name__ == "__main__":
    cycle(86400*3)
