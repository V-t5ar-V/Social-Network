import random


username = input('username: ')


users = {'lalal', '123', 'aska15', 'user', '3321'}

numbers = list(range(10))
numbers = list(map(lambda elem: str(elem), numbers))


if username in users:
    print(1)
    while True:
        print(2)
        amount = random.randint(1, 10)
        random_numbers = random.sample(numbers, amount)
        number = ''.join(random_numbers)
        new_username = username + number
        if not (new_username in users):
            username = new_username
            break
print(username)