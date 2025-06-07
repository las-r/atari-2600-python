import pygame
import time

# made by las-r on github
# v0.1

# not even close to being finished

# init pygame
pygame.init()
clock = pygame.time.Clock()

# settings
ROMFILE = ""

# display
WIDTH, HEIGHT = 128, 192
DSCALE = 4
DWIDTH, DHEIGHT = WIDTH * DSCALE, HEIGHT * DSCALE
PWIDTH, PHEIGHT = DWIDTH // WIDTH, DHEIGHT // HEIGHT

# flags
FNEGATIVE = 0x80
FOVERFLOW = 0x40
FBREAK = 0x10
FDECIMAL = 0x08
FINTERRUPT = 0x04
FZERO = 0x02
FCARRY = 0x01

# cpu
class CPU:
    # init
    def __init__(self):
        # memory
        self.mem = bytearray(65536)
        
        # registers
        self.a = 0
        self.x = 0
        self.y = 0
        self.sp = 0xfd
        self.pc = 0
        self.p = 0x24
        
    # flag funcs
    def setFlag(self, flag, cond):
        if cond:
            self.p |= flag
        else:
            self.p &= ~flag
    def getFlag(self, flag):
        return (self.p & flag) != 0
        
    # memory funcs
    def read(self, addr):
        return self.mem[addr & 0x1fff]
    def write(self, addr, val):
        self.mem[addr & 0x1fff] = val & 0xff
    def fetch(self):
        self.pc += 1
        return self.read(self.pc - 1)
    
    # operation funcs
    def ora(self, val):
        self.a |= val
        self.setFlag(FZERO, self.a == 0)
        self.setFlag(FNEGATIVE, (self.a & 0x80) != 0)
    def asl(self, val):
        carry = (val & 0x80) != 0
        val = (val << 1) & 0xFF
        self.setFlag(FCARRY, carry)
        self.setFlag(FZERO, val == 0)
        self.setFlag(FNEGATIVE, (val & 0x80) != 0)
        return val
    def and_(self, val):
        self.a &= val
        self.setFlag(FZERO, self.a == 0)
        self.setFlag(FNEGATIVE, (self.a & 0x80) != 0)
    def eor(self, val):
        self.a ^= val
        self.setFlag(FZERO, self.a == 0)
        self.setFlag(FNEGATIVE, (self.a & 0x80) != 0)
    def adc(self, val):
        carry_in = 1 if self.getFlag(FCARRY) else 0
        result = self.a + val + carry_in
        self.setFlag(FCARRY, result > 0xFF)
        overflow = (~(self.a ^ val) & (self.a ^ result)) & 0x80 != 0
        self.setFlag(FOVERFLOW, overflow)
        self.a = result & 0xFF
        self.setFlag(FZERO, self.a == 0)
        self.setFlag(FNEGATIVE, (self.a & 0x80) != 0)
    def sbc(self, val):
        carry_in = 1 if self.getFlag(FCARRY) else 0
        val ^= 0xFF  # One's complement for subtraction
        result = self.a + val + carry_in
        self.setFlag(FCARRY, result > 0xFF)
        overflow = ((result ^ self.a) & (result ^ val)) & 0x80 != 0
        self.setFlag(FOVERFLOW, overflow)
        self.a = result & 0xFF
        self.setFlag(FZERO, self.a == 0)
        self.setFlag(FNEGATIVE, (self.a & 0x80) != 0)
    def rol(self, val):
        carry_in = 1 if self.getFlag(FCARRY) else 0
        carry_out = (val & 0x80) != 0
        val = ((val << 1) & 0xFF) | carry_in
        self.setFlag(FCARRY, carry_out)
        self.setFlag(FZERO, val == 0)
        self.setFlag(FNEGATIVE, (val & 0x80) != 0)
        return val
    def lsr(self, val):
        carry_out = (val & 0x01) != 0
        val = (val >> 1) & 0xFF
        self.setFlag(FCARRY, carry_out)
        self.setFlag(FZERO, val == 0)
        self.setFlag(FNEGATIVE, False)
        return val
    def ror(self, val):
        carry_in = 1 if self.getFlag(FCARRY) else 0
        carry_out = (val & 0x01) != 0
        val = (val >> 1) | (carry_in << 7)
        self.setFlag(FCARRY, carry_out)
        self.setFlag(FZERO, val == 0)
        self.setFlag(FNEGATIVE, (val & 0x80) != 0)
        return val
    def stx(self, addr):
        self.write(addr, self.x)
    def ldx(self, val):
        self.x = val & 0xFF
        self.setFlag(FZERO, self.x == 0)
        self.setFlag(FNEGATIVE, (self.x & 0x80) != 0)
    def dec(self, val):
        val = (val - 1) & 0xFF
        self.setFlag(FZERO, val == 0)
        self.setFlag(FNEGATIVE, (val & 0x80) != 0)
        return val
    def inc(self, val):
        val = (val + 1) & 0xFF
        self.setFlag(FZERO, val == 0)
        self.setFlag(FNEGATIVE, (val & 0x80) != 0)
        return val
    
    # fetch value funcs
    def xind(self):
        zp = self.fetch()
        lo = self.read((zp + self.x) & 0xff)
        hi = self.read((zp + self.x + 1) & 0xff)
        return self.read((hi << 8) | lo)
    
    # step func
    def step(self):
        # get opcode
        opc = self.fetch()
        o0 = (opc & 0xf0) >> 4
        o1 = opc & 0x0f
        
        # run opcode
        match o0:
            case 0:
                match o1:
                    case 0: pass
                    case 1: 
                        self.ora(self.xind())
                    case 5: self.ora(self.read(self.fetch()))
                    case 6: 
                        
    # reset
    def reset(self):
        self.pc = (self.read(0xfffd) << 8) | self.read(0xfffc)
        
# main loop
cpu = CPU()
cpu.reset()
run = True
while run:
    # input events
    for event in pygame.event.get():
        # quit event
        if event.type == pygame.QUIT:
            run = False
            
    # cpu step
    cpu.step()
    
    # fps
    clock.tick(60)
            
# quit
pygame.quit()
