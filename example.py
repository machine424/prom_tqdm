from time import sleep

from prom_tqdm import prom_tqdm

TOTO = 1000000

with prom_tqdm(
    task_name="my_task", push_gateway="http://localhost:12347", total=TOTO
) as progress_bar:
    for i in range(TOTO):
        sleep(0.0001)
        progress_bar.update(1)
