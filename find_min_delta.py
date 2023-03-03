from birdcage import *

if __name__ == "__main__":
    # Run some random games and see what the difference between
    # the top two distinct voltage differences is, when measured using
    # a 10-bit analog to digital converter (like the Arduino).

    resolution = 1024

    min_delta = resolution

    for i in range(10):
        print(i)
        bc = BirdCage(M=4)
        s = Shannon()
        p1 = Random()
        p2 = Random()

        while not (bc.white_has_won() or bc.black_has_won()):
            voltage_diffs = s._get_voltage_diffs(bc)
            distinct = set(voltage_diffs.values())
            distinct_sorted = sorted([(v * resolution).evalf() for v in distinct if v > 0], reverse=True)
            if len(distinct_sorted) > 1:
                delta = distinct_sorted[0] - distinct_sorted[1]
                if delta < min_delta:
                    min_delta = delta
                    print(min_delta)
                    print(bc)

            move = p1.play(bc)
            bc.move(move)

            move = p2.play(bc)
            bc.move(move)

        print("min_delta", min_delta)