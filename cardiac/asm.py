from cmd import Cmd
from cStringIO import StringIO
import shlex, sys

class AsmError(Exception):
    pass

class Assembler(Cmd):
    """
    Please do not use this class yet, it is not complete!
    I am sure this could be done better with say GNU Bison or Yacc,
    but that's more complicated than needed for a simple assembler.
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
        self.pc = 0 #: Allows us to keep track of the program pointer.
        self.var_map = {} #: This is used to keep track of variables.
        self.labels = {} #: Stores the label names, and where they point to.
        self.buffer = StringIO() #: This is our buffer where we will store the CARDIAC deck
        self.size = 0
    def emptyline(self):
        """ This is requried due to how the Python Cmd module works... """
        pass
    def unknown_command(self, line):
        self.stdout.write('*** Unknown syntax: %s\n'%line)
    @property
    def ptr(self):
        """ This will always give the proper pointer in the deck. """
        if self.addr:
            return self.addr
        return self.pc
    def write_cards(self, *card_list):
        """ Helper fuction to make life easier. """
        for card in card_list:
            self.buffer.write('%s\n' % card)
        self.pc += len(card_list) #: Increment the program pointer.
    def write_addr(self):
        """ This method will only write out the address if we're in that mode. """
        if self.addr:
            self.write_cards('0%s' % self.addr)
            self.addr +=1
        self.size +=1
    def do_exit(self, args):
        return True
    def do_bootstrap(self, args):
        """ Places some basic bootstrap code in. """
        self.addr = 10
        self.start = self.addr #: Updates all required address variables.
        self.write_cards('002', '800')
        self.pc = self.start
    def do_bootloader(self, args):
        """ Places some basic bootstrap code in. """
        self.write_cards('002', '800') 
        addr = 89 #: This is the start address of the bootloader code.
        for card in ('001', '189', '200', '689', '198', '700', '698', '301', '889', 'SIZE'):
            self.write_cards('0%s' % addr, card)
            addr+=1
        self.write_cards('002', '889')
        self.pc = 1
    def do_end(self, args):
        """ Finalizes your code. """
        for var in self.var_map:
            ptr = self.padding+str(self.ptr)
            self.write_addr()
            self.write_cards(self.var_map[var][-3:])
            self.labels[var] = ptr[-2:]
        if self.start:
            self.write_cards('002', '8%s' % self.start)
        self.buffer.seek(0)
        buf = StringIO()
        for card in self.buffer.readlines():
            if card[1] == '*': #: We have a label.
                card = '%s%s\n' % (card[0], self.labels[card[2:-1]])
            elif card[:4] == 'SIZE':
                card = '000'+str(self.size-1)
                card = '%s\n' % card[-3:]
            buf.write(card)
        buf.seek(0)
        print ''.join(buf.readlines())
        return True
    def do_var(self, args):
        """ Creates a named variable reference in memory, a simple pointer. """
        s = shlex.split(args)
        if len(s) != 3 or s[1] != '=':
            raise AsmError('Incorrect format of the "var" statement.')
        if s[0] in self.var_map:
            raise AsmError('Variable has been declared twice!')
        value = int(s[2])
        self.var_map[s[0]] = '000'+str(value)
    def do_label(self, args):
        """ Creates a named label reference in memory, a simple pointer. """
        if args == '':
            raise AsmError('Incorrect format of the "label" statement.')
        if args in self.labels:
            raise AsmError('Label has been declared twice!')
        ptr = '00'+str(self.ptr)
        self.labels[args] = ptr[-2:]
    def default(self, line):
        """ This method is the actual lexical parser for the assembly. """
        if line.startswith('#'):
            return
        s = shlex.split(line)
        op, arg = s[0].lower(), '00'
        if len(s) == 2:
            if s[1].startswith('$'):
                arg = '*%s' % s[1][1:]
            else:
                arg = self.padding+s[1]
                arg = arg[-2:]
        if op in self.op_map:
            self.write_addr()
            self.write_cards('%s%s' % (self.op_map[op], arg))
        else:
            self.unknown_command(line)

def main():
    try:
        asm = Assembler()
        src = 'deck1.asm'
        if len(sys.argv) > 1:
            src = sys.argv[1]
        asm.configure()
        for line in open(src, 'r').readlines():
            asm.cmdqueue.append(line)
        asm.cmdloop()
    except AsmError, e:
        print "Asm Error: %s" % e

if __name__ == '__main__':
    main()
