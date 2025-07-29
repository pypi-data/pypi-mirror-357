class WaitBarConsole:
    @staticmethod
    def print_bar_text(text):
        print(text)

    @staticmethod
    def print_wait_bar(i, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
        """
        This function will print a waitbar in the console
        Variables:
        i -- Iteration number
        total -- Total iterations
        front text -- Name in front of bar
        prefix -- Name after bar
        suffix -- Decimals of percentage
        length -- width of the waitbar
        fill -- bar fill
        """
        import sys

        # total can never be zero because we divide by total
        if total == 0:
            total = 0.0001

        percent = ("{0:." + str(decimals) + "f}").format(100 * (i / float(total)))
        filled = int(length * i // total)
        bar = fill * filled + '-' * (length - filled)

        sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
        sys.stdout.flush()

        if i == total:
            print()
