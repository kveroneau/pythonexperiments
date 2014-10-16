from cmd import Cmd
from cStringIO import StringIO
import math, shlex

class ConfigurationError(Exception):
    pass

class CPUException(Exception):
    pass

class MemoryOutOfRange(CPUException):
    pass

class InvalidOperation(CPUException):
    pass

class Asmembler(Cmd):
    """
    Please do not use this class yet, it is not complete!
    """
    op_map = {
        'inp': 0,
        'cla': 1,
        'add': 2,
        'tac': 3,
        'sft': 4,
        'out': 5,
        'sto': 6,
        'sub': 7,
        'jmp': 8,
        'hrs': 9,
    }
    padding = '00'
    def configure(self):
        self.start = self.addr = None
        self.var_map = {}
        self.buffer = StringIO()
    def emptyline(self):
        pass
    def unknown_command(self, line):
        self.stdout.write('*** Unknown syntax: %s\n'%line)
    def do_exit(self, args):
        return True
    def do_bootstrap(self, args):
        """ Places some basic bootstrap code in. """
        if args == '':
            self.addr = 10
        else:
            self.addr = int(args)
        self.start = self.addr
        self.stdout.write('002\n800\n')
    def do_end(self, args):
        """ Finalizes your code. """
        if start:
            self.stdout.write('002\n8%s\n' % self.start)
    def default(self, line):
        s = shlex.split(line)
        op, arg = s[0], '00'
        if len(s) == 2:
            arg = self.padding+s[1]
            arg = arg[-2:]
        if op in self.op_map:
            if addr:
                self.stdout.write('0%s\n' % self.addr)
                self.addr +=1
            self.stdout.write('%s%s\n' % (self.op_map[op], arg))

class Memory(object):
    """
    This class controls the virtual memory space of the simulator.
    """
    def init_mem(self):
        """
        This method resets the Cardiac's memory space to all blank strings, as per Cardiac specs.
        """
        self.mem = ['' for i in range(0,100)]
        self.mem[0] = '001' #: The Cardiac bootstrap operation.
    def get_memint(self, data):
        """
        Since our memory storage is *string* based, like the real Cardiac, we need
        a reusable function to grab a integer from memory.  This method could be
        overridden if say a new memory type was implemented, say an mmap one.
        """
        return int(self.get_mem(data))
    def chk_addr(self, addr):
        """
        This method keeps things DRY and clean, so we don't need to trap IndexError
        exceptions and the like.
        """
        addr = int(addr) # Sanitize before use.
        if addr < 0 or addr > len(self.mem)-1:
            raise MemoryOutOfRange('Memory out of Range: %s' % addr)
    def get_mem(self, data):
        """
        This method controls memory access to obtain a single address.
        """
        self.chk_addr(data)
        return self.mem[data]
    def set_mem(self, addr, data):
        """
        This method controls memory writr access to a single address.
        """
        self.chk_addr(addr)
        self.mem[addr] = self.pad(data)
    def pad(self, data, length=3):
        """
        This function pads either an integer or a number in string format with
        zeros.  This is needed to replicate the exact behavior of the Cardiac.
        """
        orig = int(data)
        padding = '0'*length
        data = '%s%s' % (padding, abs(orig))
        if orig < 0:
            return '-'+data[-length:]
        return data[-length:]

class IO(object):
    """
    This class controls the virtual I/O of the simulator.
    To enable alternate methods of input and output, swap this.
    """
    def init_reader(self):
        """
        This method initializes the input reader.
        """
        self.reader = [] #: This variable can be accessed after initializing the class to provide input data.
    def init_output(self):
        """
        This method initializes the output deck/paper/printer/teletype/etc...
        """
        self.output = []
    def read_deck(self, fname):
        """
        This method will read a list of instructions into the reader.
        """
        self.reader = [s.rstrip('\n') for s in open(fname, 'r').readlines()]
        self.reader.reverse()
    def format_output(self):
        """
        This method is to format the output of this virtual IO device.
        """
        return '\n'.join(self.output)
    def get_input(self):
        """
        This method is used to get input from this IO device, this could say
        be replaced with raw_input() to manually enter in data.
        """
        try:
            return self.reader.pop()
        except IndexError:
            # Fall back to raw_input() in the case of EOF on the reader.
            return raw_input('INP: ')[:3]
    def stdout(self, data):
        self.output.append(data)

class CPU(object):
    """
    This class is the cardiac "CPU".
    """
    def __init__(self):
        self.init_cpu()
        self.reset()
        try:
            self.init_mem()
        except AttributeError:
            raise ConfigurationError('You need to Mixin a memory-enabled class.')
        try:
            self.init_reader()
            self.init_output()
        except AttributeError:
            raise ConfigurationError('You need to Mixin a IO-enabled class.')
    def reset(self):
        """
        This method resets the CPU's registers to their defaults.
        """
        self.pc = 0 #: Program Counter
        self.ir = 0 #: Instruction Register
        self.acc = 0 #: Accumulator
        self.running = False #: Are we running?
    def init_cpu(self):
        """
        This fancy method will automatically build a list of our opcodes into a hash.
        This enables us to build a typical case/select system in Python and also keeps
        things more DRY.  We could have also used the getattr during the process()
        method before, and wrapped it around a try/except block, but that looks
        a bit messy.  This keeps things clean and simple with a nice one-to-one
        call-map. 
        """
        self.__opcodes = {}
        classes = [self.__class__] #: This holds all the classes and base classes.
        while classes:
            cls = classes.pop() # Pop the classes stack
            if cls.__bases__: # Does this class have any base classes?
                classes = classes + list(cls.__bases__)
            for name in dir(cls): # Lets iterate through the names.
                if name[:7] == 'opcode_': # We only want opcodes here.
                    try:
                        opcode = int(name[7:])
                    except ValueError:
                        raise ConfigurationError('Opcodes must be numeric, invalid opcode: %s' % name[7:])
                    self.__opcodes.update({opcode:getattr(self, 'opcode_%s' % opcode)})
    def fetch(self):
        """
        This method retrieves an instruction from memory address pointed to by the program pointer.
        Then we increment the program pointer.
        """
        self.ir = self.get_memint(self.pc)
        self.pc +=1
    def process(self):
        """
        Process a single opcode from the current program counter.  This is
        normally called from the running loop, but can also be called
        manually to provide a "step-by-step" debugging interface, or
        to slow down execution using time.sleep().  This is the method
        that will also need to used if you build a TK/GTK/Qt/curses frontend
        to control execution in another thread of operation.
        """
        self.fetch()
        opcode, data = int(math.floor(self.ir / 100)), self.ir % 100
        if self.__opcodes.has_key(opcode):
            self.__opcodes[opcode](data)
        else:
            raise InvalidOperation('Invalid OpCode detected: %s' % opcode)
    def run(self, pc=None):
        """ Runs code in memory until halt/reset opcode. """
        if pc:
            self.pc = pc
        self.running = True
        while self.running:
            self.process()
        print "Output:\n%s" % self.format_output()
        self.init_output()

class Cardiac(CPU, Memory, IO):
    """
    This class contains the actual opcodes needed to run Cardiac machine code.
    """
    def opcode_0(self, data):
        """ INPUT Operation """
        self.set_mem(data, self.get_input())
    def opcode_1(self, data):
        """ Clear and Add Operation """
        self.acc = self.get_memint(data)
    def opcode_2(self, data):
        """ Add Operation """
        self.acc += self.get_memint(data)
    def opcode_3(self, data):
        """ Test Accumulator contents Operation """
        if self.acc < 0:
            self.pc = data
    def opcode_4(self, data):
        """ Shift operation """
        x,y = int(math.floor(data / 10)), int(data % 10)
        for i in range(0,x):
            self.acc = (self.acc * 10) % 10000
        for i in range(0,y):
            self.acc = int(math.floor(self.acc / 10))
    def opcode_5(self, data):
        """ Output operation """
        self.stdout(self.get_mem(data))
    def opcode_6(self, data):
        """ Store operation """
        self.set_mem(data, self.acc)
    def opcode_7(self, data):
        """ Subtract Operation """
        self.acc -= self.get_memint(data)
    def opcode_8(self, data):
        """ Unconditional Jump operation """
        self.pc = data
    def opcode_9(self, data):
        """ Halt and Reset operation """
        self.reset()

def main():
    try:
        c = Cardiac()
        c.read_deck('deck1.txt')
        c.run()
    except ConfigurationError, e:
        print "Configuration Error: %s" % e
    except CPUException, e:
        # Here we trap all exceptions which can be triggered by user code, and display an error to the end-user.
        print "IR: %s\nPC: %s\nACC: %s" % (c.ir, c.pc, c.acc)
        print str(e)
    except:
        # For every other exceptions, which are normally Python related, we display it.
        print "IR: %s\nPC: %s\nOutput: %s\n" % (c.ir, c.pc, c.format_output())
        raise    

if __name__ == '__main__':
    main()
