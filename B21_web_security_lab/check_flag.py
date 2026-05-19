import hashlib

task1_hash = "249e93d8320050c2add1ae209d0698200dbaf5e101607abb9f2082c1372057d1"
task2_hash = "e0350676b80449cc335361a55e1ba61b4939b8057a8523868c640c3e11674fc4"

def check_flag_1(user_input):
    input_hash = hashlib.sha256(user_input.encode()).hexdigest()
    if input_hash == task1_hash:
        print("Correct flag!")
        return True
    print("Incorrect flag.")
    return False

def check_flag_2(user_input):
    input_hash = hashlib.sha256(user_input.encode()).hexdigest()
    if input_hash == task2_hash:
        print("Correct flag!")
        return True
    print("Incorrect flag.")
    return False


flag1 = input("Enter flag for Task 1: ")
check1 = check_flag_1(flag1)

flag2 = input("Enter flag for Task 2: ")
check2 = check_flag_2(flag2)

if check1 and check2:
    print("ALL COMPLETED")
