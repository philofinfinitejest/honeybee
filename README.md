honeybee
========

Wraps the python multiprocessing library to coordinate chained worker tasks that rely on each others outputs as inputs.

Example code:

    from honeybee import Hive, Worker
    import logging

    FORMAT = '%(asctime)-15s %(levelname)-8s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)

    def fizz(args):
        return "fizz"

    def buzz(args):
        return "buzz"

    def uzz(args):
        raise Exception()

    def kick_hive(args):
        return "KICK!!!"

    def run_away(args):
        return "Aiiiiiii!"

    def observe(args):
        print("\n".join(a if a is not None else "Error" for a in args))

    if __name__ == "__main__":
        hive = Hive('comedy', 5)
        prime_mover = Worker("kick", hive, kick_hive)
        bees = [Worker('bee', hive, fizz, [prime_mover]), Worker('bee', hive, buzz, [prime_mover]),
                    Worker('bee', hive, fizz, [prime_mover]), Worker('bee', hive, buzz, [prime_mover]),
                    Worker('bee', hive, fizz, [prime_mover]), Worker('bee', hive, buzz, [prime_mover]),
                    Worker('bee', hive, fizz, [prime_mover]), Worker('bee', hive, buzz, [prime_mover]),
                    Worker('bee', hive, fizz, [prime_mover]), Worker('bee', hive, buzz, [prime_mover]),
                    Worker('bee', hive, uzz, [prime_mover]),
                    ]
        what_a_work_is_man = Worker('man', hive, run_away, bees)
        observer = Worker('observer', hive, observe, [prime_mover] + bees + [what_a_work_is_man])
        workers = [prime_mover, what_a_work_is_man, observer] + bees
        hive.run(workers)