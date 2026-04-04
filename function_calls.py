"""
函数调用模块
包含所有业务函数，互相调用，并打印日志
不关心日志格式，只关注业务逻辑
"""

import random
from loguru import logger

# 调用深度计数器
call_depth = 0
MAX_DEPTH = 20


def log_entry(func_name):
    """记录函数进入日志"""
    global call_depth
    call_depth += 1
    logger.debug(f"▶ 进入函数: {func_name} | 当前深度: {call_depth}")


def log_exit(func_name):
    """记录函数退出日志"""
    global call_depth
    logger.debug(f"◀ 退出函数: {func_name} | 当前深度: {call_depth}")
    call_depth -= 1


def should_return():
    """判断是否应该返回(达到最大深度)"""
    return call_depth >= MAX_DEPTH


def func_a():
    """函数A - 可能调用func_b或func_c"""
    log_entry("func_a")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_a")
        return

    choice = random.choice(['b', 'c', 'd'])
    if choice == 'b':
        func_b()
    elif choice == 'c':
        func_c()
    else:
        func_d()

    log_exit("func_a")


def func_b():
    """函数B - 可能调用func_a或func_e或func_f"""
    log_entry("func_b")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_b")
        return

    choice = random.choice(['a', 'e', 'f'])
    if choice == 'a':
        func_a()
    elif choice == 'e':
        func_e()
    else:
        func_f()

    log_exit("func_b")


def func_c():
    """函数C - 可能调用func_d或func_g或func_h"""
    log_entry("func_c")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_c")
        return

    choice = random.choice(['d', 'g', 'h'])
    if choice == 'd':
        func_d()
    elif choice == 'g':
        func_g()
    else:
        func_h()

    log_exit("func_c")


def func_d():
    """函数D - 可能调用func_a或func_e或func_i"""
    log_entry("func_d")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_d")
        return

    choice = random.choice(['a', 'e', 'i'])
    if choice == 'a':
        func_a()
    elif choice == 'e':
        func_e()
    else:
        func_i()

    log_exit("func_d")


def func_e():
    """函数E - 可能调用func_b或func_f或func_j"""
    log_entry("func_e")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_e")
        return

    choice = random.choice(['b', 'f', 'j'])
    if choice == 'b':
        func_b()
    elif choice == 'f':
        func_f()
    else:
        func_j()

    log_exit("func_e")


def func_f():
    """函数F - 可能调用func_c或func_g或func_k"""
    log_entry("func_f")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_f")
        return

    choice = random.choice(['c', 'g', 'k'])
    if choice == 'c':
        func_c()
    elif choice == 'g':
        func_g()
    else:
        func_k()

    log_exit("func_f")


def func_g():
    """函数G - 可能调用func_a或func_d或func_l"""
    log_entry("func_g")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_g")
        return

    choice = random.choice(['a', 'd', 'l'])
    if choice == 'a':
        func_a()
    elif choice == 'd':
        func_d()
    else:
        func_l()

    log_exit("func_g")


def func_h():
    """函数H - 可能调用func_b或func_e或func_m"""
    log_entry("func_h")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_h")
        return

    choice = random.choice(['b', 'e', 'm'])
    if choice == 'b':
        func_b()
    elif choice == 'e':
        func_e()
    else:
        func_m()

    log_exit("func_h")


def func_i():
    """函数I - 可能调用func_c或func_f或func_n"""
    log_entry("func_i")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_i")
        return

    choice = random.choice(['c', 'f', 'n'])
    if choice == 'c':
        func_c()
    elif choice == 'f':
        func_f()
    else:
        func_n()

    log_exit("func_i")


def func_j():
    """函数J - 可能调用func_d或func_g或func_o"""
    log_entry("func_j")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_j")
        return

    choice = random.choice(['d', 'g', 'o'])
    if choice == 'd':
        func_d()
    elif choice == 'g':
        func_g()
    else:
        func_o()

    log_exit("func_j")


def func_k():
    """函数K - 可能调用func_a或func_h或func_p"""
    log_entry("func_k")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_k")
        return

    choice = random.choice(['a', 'h', 'p'])
    if choice == 'a':
        func_a()
    elif choice == 'h':
        func_h()
    else:
        func_p()

    log_exit("func_k")


def func_l():
    """函数L - 可能调用func_b或func_i或func_q"""
    log_entry("func_l")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_l")
        return

    choice = random.choice(['b', 'i', 'q'])
    if choice == 'b':
        func_b()
    elif choice == 'i':
        func_i()
    else:
        func_q()

    log_exit("func_l")


def func_m():
    """函数M - 可能调用func_c或func_j或func_r"""
    log_entry("func_m")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_m")
        return

    choice = random.choice(['c', 'j', 'r'])
    if choice == 'c':
        func_c()
    elif choice == 'j':
        func_j()
    else:
        func_r()

    log_exit("func_m")


def func_n():
    """函数N - 可能调用func_d或func_k或func_s"""
    log_entry("func_n")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_n")
        return

    choice = random.choice(['d', 'k', 's'])
    if choice == 'd':
        func_d()
    elif choice == 'k':
        func_k()
    else:
        func_s()

    log_exit("func_n")


def func_o():
    """函数O - 可能调用func_e或func_l或func_t"""
    log_entry("func_o")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_o")
        return

    choice = random.choice(['e', 'l', 't'])
    if choice == 'e':
        func_e()
    elif choice == 'l':
        func_l()
    else:
        func_t()

    log_exit("func_o")


def func_p():
    """函数P - 可能调用func_f或func_m或func_a"""
    log_entry("func_p")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_p")
        return

    choice = random.choice(['f', 'm', 'a'])
    if choice == 'f':
        func_f()
    elif choice == 'm':
        func_m()
    else:
        func_a()

    log_exit("func_p")


def func_q():
    """函数Q - 可能调用func_g或func_n或func_b"""
    log_entry("func_q")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_q")
        return

    choice = random.choice(['g', 'n', 'b'])
    if choice == 'g':
        func_g()
    elif choice == 'n':
        func_n()
    else:
        func_b()

    log_exit("func_q")


def func_r():
    """函数R - 可能调用func_h或func_o或func_c"""
    log_entry("func_r")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_r")
        return

    choice = random.choice(['h', 'o', 'c'])
    if choice == 'h':
        func_h()
    elif choice == 'o':
        func_o()
    else:
        func_c()

    log_exit("func_r")


def func_s():
    """函数S - 可能调用func_i或func_p或func_d"""
    log_entry("func_s")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_s")
        return

    choice = random.choice(['i', 'p', 'd'])
    if choice == 'i':
        func_i()
    elif choice == 'p':
        func_p()
    else:
        func_d()

    log_exit("func_s")


def func_t():
    """函数T - 可能调用func_j或func_q或func_e"""
    log_entry("func_t")

    if should_return():
        logger.debug("  达到最大深度,返回")
        log_exit("func_t")
        return

    choice = random.choice(['j', 'q', 'e'])
    if choice == 'j':
        func_j()
    elif choice == 'q':
        func_q()
    else:
        func_e()

    log_exit("func_t")


def main():
    """主函数 - 随机调用其他函数"""
    logger.debug("=" * 80)
    logger.debug("程序开始执行 - 使用loguru日志库")
    logger.debug("=" * 80)

    # 主函数随机选择一个函数开始调用
    functions = [
        func_a, func_b, func_c, func_d, func_e,
        func_f, func_g, func_h, func_i, func_j,
        func_k, func_l, func_m, func_n, func_o,
        func_p, func_q, func_r, func_s, func_t
    ]

    # 随机选择一个函数开始
    start_func = random.choice(functions)
    logger.debug(f"随机选择起始函数: {start_func.__name__}")

    # 调用起始函数
    start_func()

    # 随机选择一个函数开始
    start_func = random.choice(functions)
    logger.debug(f"随机选择起始函数: {start_func.__name__}")

        # 调用起始函数
    start_func()

    # 随机选择一个函数开始
    start_func = random.choice(functions)
    logger.debug(f"随机选择起始函数: {start_func.__name__}")


    # 调用起始函数
    start_func()

    logger.debug("=" * 80)
    logger.debug("程序执行完毕")
    logger.debug("=" * 80)


if __name__ == "__main__":
    # 设置随机种子(可选,用于复现结果)
    # random.seed(42)

    main()
