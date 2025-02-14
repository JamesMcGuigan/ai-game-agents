import random

def random_agent_unseeded(observation, configuration):
    # Reset seed using system clock
    if observation.step == 0:
        random.seed(None)

    action = random.randint(0, configuration.signs-1)
    print(f'random_agent_unseeded() = {action}')
    return int(action)
