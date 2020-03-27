"""CPU functionality.

Constructor method not filled out.
Load method filled out and straight forward from Monday class
Alu method ADD completed, needs the rest of the mathematical operations
Trace method filled out so print out cpu state, useful for debugging
Run method to be completed, will run the program from load
"""


import sys


class CPU:
    """Main CPU class."""

    SP = 7
    # OP codes
    HLT = 0b00000001
    PRN = 0b01000111
    LDI = 0b10000010
    MUL = 0b10100010
    PUSH = 0b01000101
    POP = 0b01000110
    ADD = 0b10100000
    CALL = 0b01010000
    RET = 0b00010001
    CMP = 0b10100111
    JMP = 0b01010100
    JEQ = 0b01010101
    JNE = 0b01010110

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.flags = 0
        self.branchtable = {}

        # Insert OP codes into branchtable
        # Values point to f(x) for carrying out OP code
        self.branchtable[CPU.PRN] = self._handle_prn
        self.branchtable[CPU.LDI] = self._handle_ldi
        self.branchtable[CPU.PUSH] = self._handle_push
        self.branchtable[CPU.POP] = self._handle_pop
        self.branchtable[CPU.HLT] = self._handle_hlt
        self.branchtable[CPU.CALL] = self._handle_call
        self.branchtable[CPU.RET] = self._handle_ret
        self.branchtable[CPU.CMP] = self._handle_cmp
        self.branchtable[CPU.JMP] = self._handle_jmp
        self.branchtable[CPU.JEQ] = self._handle_jeq
        self.branchtable[CPU.JNE] = self._handle_jne

    def load(self):
        if len(sys.argv) < 2:
            print("Usage: ls8.py filename")
            sys.exit(1)

        filename = sys.argv[1]
        index = 0
        try:
            with open(filename) as f:

                for line in f:
                    command = line.split("#")[0].strip()
                    if command == "":
                        continue

                    num = int(command, 2)
                    self.ram[index] = num
                    index += 1

        except FileNotFoundError:
            print("File not found.")

    def _handle_hlt(self):
        return (self.pc, False)

    def _handle_prn(self):
        reg_a = self.ram_read(self.pc + 1)
        print(self.register[reg_a])
        self.pc += 2
        return (self.pc, True)

    def _handle_ldi(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.register[reg_a] = reg_b
        self.pc += 3
        return (self.pc, True)

    def _handle_push(self):
        reg_a = self.ram_read(self.pc + 1)
        val = self.register[reg_a]

        self.register[CPU.SP] -= 1
        self.ram[self.register[CPU.SP]] = val

        self.pc += 2
        return (self.pc, True)

    def _handle_pop(self):
        reg_a = self.ram_read(self.pc + 1)
        val = self.ram[self.register[CPU.SP]]

        self.register[reg_a] = val
        self.register[CPU.SP] += 1

        self.pc += 2
        return (self.pc, True)

    def _handle_call(self):
        # Grab the value in register that refers to called function
        reg = self.ram_read(self.pc + 1)
        # Grab next command in op to return to after function
        next_op = self.pc + 2
        # Move PC to address in register
        self.pc = self.register[reg]
        # Push next op to stack
        self.register[CPU.SP] -= 1
        self.ram[self.register[CPU.SP]] = next_op

        return (self.pc, True)

    def _handle_ret(self):
        # Pop value from stack, store as PC
        self.pc = self.ram[self.register[CPU.SP]]
        self.register[CPU.SP] += 1

        return (self.pc, True)

    def _handle_cmp(self):
        # Get next 2 values in program
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        # From register, grab values of each
        val_a = self.register[reg_a]
        val_b = self.register[reg_b]
        # compare values
        # if equal, set flag to 1
        if val_a == val_b:
            self.flags = 0b1
        # if a > b, set flag equal to 2
        elif val_a > val_b:
            self.flags = 0b10
        # if b > a, set flag to 4
        elif val_b > val_a:
            self.flags = 0b100
        # increment pc by 3
        self.pc += 3
        return (self.pc, True)

    def _handle_jmp(self):
        # read next arg from ram
        reg_a = self.ram_read(self.pc + 1)
        # set pc equal to value in register at index of arg
        self.pc = self.register[reg_a]

        return (self.pc, True)

    def _handle_jeq(self):
        # check if equal flag is on
        # if not...
        if not self.flags & 0b1:
            # increment pc by 2
            self.pc += 2
            # return
            return (self.pc, True)
        # if yes...
        elif self.flags & 0b1:
            # read next arg from ram
            reg_a = self.ram_read(self.pc + 1)
            # set pc equal to value in register at index of arg
            self.pc = self.register[reg_a]
            # return
            return (self.pc, True)

    def _handle_jne(self):
        # Check if equal flag on
        # if yes...
        if self.flags & 0b1:
            # increment pc by 2
            self.pc += 2
            # return
            return (self.pc, True)
        # if not...
        elif not self.flags & 0b0:
            # read next arg from ram
            reg_a = self.ram_read(self.pc + 1)
            # set pc equal to value in register at index of arg
            self.pc = self.register[reg_a]
            # return
            return (self.pc, True)

    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, index, value):
        self.ram[index] = value

    def alu(self, op):
        """ALU operations."""
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        if op == CPU.ADD:
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == CPU.MUL:
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

        self.pc += 3
        return (self.pc, True)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        alu_ops = [CPU.MUL, CPU.ADD]
        running = True

        while running:
            ir = self.ram[self.pc]

            try:
                if ir in alu_ops:
                    output = self.alu(ir)
                    self.pc = output[0]
                    running = output[1]
                else:
                    output = self.branchtable[ir]()
                    self.pc = output[0]
                    running = output[1]

            except KeyError:
                print(f"ERROR: Instruction {ir} not recognized. Program exiting.")
                sys.exit(1)
