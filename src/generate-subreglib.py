#!/usr/bin/env python3

# This script produces dozens of PLEB files
# systematically covering certain interesting subregular classes.

# 64 symbols over which constraints may be derived
symbols = ["a","b","c","d","e","f","g","h","i","j","k","l","m",
           "n","o","p","q","r","s","t","u","v","w","x","y","z",
           "A","B","C","D","E","F","G","H","I","J","K","L","M",
           "N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
           "á","à","ǎ","é","è","ě","ó","ò","ǒ","ú","ù","ǔ"
           ]

# the output directory
dir = "subreglib"

# we'll define the symbols in files that can be included,
# so that an alphabet can be imported and contraints can omit slashes
def symbolDefs(syms):
    """
    define the given number of symbols.

    syms: the number of symbols
    """
    a=[]
    for x in symbols[:syms]:
        a.append("=" + x + "{/" + x + "}")
    return "\n".join(a)

def universalOCP(syms, width=2, sep=" "):
    """
    forbid factors of the given width
    consisting of all the same symbol,
    for the given number of symbols.

     syms: the number of symbols (times two)
    width: the size of the factor
      sep: " " for successor or "," for general precedence
    """
    if syms == 0:
        return "<>"
    a=[]
    for i in range(0,syms,2):
        a.append("<" + sep.join(width*[symbols[i]]) + ">")
    return "~\\/{" + ",".join(a) + "}"

def fullAlternation(syms, width=2, sep=" "):
    """
    forbid factors of the given width
    consisting of an alternating sequence of adjacent symbols,
    for the given number of symbols.
    for example, "abab" for syms=2 and width=4.

     syms: the number of symbols
    width: the size of the factor
      sep: " " for successor or "," for general precedence
    """
    if syms == 0:
        return "<>"
    a=[]
    for i in range(0,syms,2):
        a.append("<" + sep.join(width//2*[symbols[i],symbols[i+1]]) + ">")
        a.append("<" + sep.join(width//2*[symbols[i+1],symbols[i]]) + ">")
    return "~\\/{" + ",".join(a) + "}"

def halfAlternation(syms, width=2, sep=" "):
    """
    like fullAlternation but only in one direction
    """
    if syms == 0:
        return "<>"
    a=[]
    for i in range(0,syms,2):
        a.append("<" + sep.join(width//2*[symbols[i],symbols[i+1]]) + ">")
    return "~\\/{" + ",".join(a) + "}"

def tierify(sigma, tau, expr):
    """
    if sigma and tau are inequal, put things on a tier!
    """
    if sigma == tau:
        return expr
    return "[%s]%s" % (",".join(symbols[:tau]),expr)

def writeFile(sigma,tau,cls,k,t,i,expr):
    """
    sigma: two-digit number of symbols in the alphabet
      tau: two-digit number of symbols on the tier (= Sigma if no tier)
      cls: the type of language
        k: the width of factors involved
        t: the largest distinguished multiplicity
           t=1 for things lower than LTT, and t=j for LPT
        i: one-digit identifier for the language
     expr: the expression to use
    """
    if ((cls in ["SP","PT"])
        and sigma != tau):
        return
    prefix=""
    if sigma != tau:
        prefix = "T"
    bn="%02d.%02d.%s.%d.%d.%d"%(sigma,tau,prefix + cls,k,t,i)
    f = open("%s/%s.plebby" % (dir,bn), "w")
    f.write(':import "syms%02d.plebby"\n'%sigma)
    f.write(tierify(sigma,tau,expr) + "\n")
    f.write(':writeATT "../fstlib/att_format/%s.att" _ _ it\n' % bn)
    f.close()

def boundaryCondition(expr,width=2,sep=" "):
    """
    must start with width-1 of the symbol (a)
    for piecewise expressions, this is replaced by
    forbidding the subsequence defined by
    (c) followed by width-1 of the symbol (a)
    """
    g = "%%|<%s>" % sep.join((width-1) * [symbols[0]])
    if sep == ",":
        g = "~<%s>" % (sep.join([symbols[2]] + (width-1) * [symbols[0]]))
    return "/\\{%s,%s}" % (g, expr)

def notEndA(width=2,sep=" "):
    """
    must not end with width-1 instances of (a)
    for piecewise expressions, this is replaced by
    forbidding the subsequence defined by
    (c) followed by width-1 of the symbol (a)
    """
    g = "~|%%<%s>" % sep.join((width-1) * [symbols[0]])
    if sep == ",":
        g = "~<%s>" % ([symbols[2]] + [sep.join((width-1) * [symbols[0]])])
    return g

def endB(width=2,sep=" "):
    """
    must end with width-1 instances of (b)
    for piecewise expressions, this is replaced by
    forbidding the subsequence defined by
    width-1 of the symbol (b) followed by (c)
    """
    g = "|%%<%s>" % sep.join((width-1) * [symbols[1]])
    if sep == ",":
        g = "~<%s>" % (sep.join((width-1) * [symbols[1]] + [symbols[2]]))
    return g

def union(*args):
    """
    Satisfied if any of the given expressions are satisfied
    """
    return "\\/{" + ",".join(args) + "}"

def intersection(*args):
    """
    Satisfied if all of the given expressions are satisfied
    """
    return "/\\{" + ",".join(args) + "}"

def implication(a, b):
    """
    Satisfied iff the first expression is false or the second is true
    """
    return union("~"+a, b)

def biimplication(a, b):
    """
    Satisfied iff implication(a,b) is AND implication(b,a) is
    """
    return intersection(implication(a,b),implication(b,a))

def ak(k):
    """
    A substring of k-many instances of "a" occurs
    """
    return "<" + " ".join(k*[symbols[0]]) + ">"

def altk(base,k):
    """
    A k-wide substring of alternating (a,b) or (c,d) etc occurs.
    """
    a=[]
    for i in range(0,base,2):
        a.append("<" + " ".join((k//2)*[symbols[i],symbols[i+1]]) + ">")
    return union(*a)

def leastn(n,expr):
    """
    The given expression occurs n or more times
    """
    return "@(" + ",".join(n*[expr]) + ")"

def leastnOr1(n,expr):
    """
    The given expression occurs exactly once, or at least n times,
    nothing in between.
    """
    return union(intersection(expr,"~"+leastn(2,expr)),leastn(n,expr))

def gapAlt(syms,k,j=None):
    """
    Forbid a^k followed by b^k etc, through the number of symbols, cycled,
    but restricted to j-many blocks.

    syms=2, j=k=2: ~<a a,b b>
    syms=2, j=k=4: ~<a a a a,b b b b,a a a a,b b b b>
    syms=4, j=k=4: ~<a a a a,b b b b,c c c c,d d d d>
    syms=4, j=4, k=2: ~<a a,b b,c c,d d>
    """
    if type(j)==type(None):
        j=k
    return "~<" + ",".join((j*list(map(lambda x:" ".join(k*[x]),
                                      symbols[:syms])))[:j]) + ">"

def lp(xs):
    """
    xs: a list of lists
    each inner list is a substring part and they are separated by gaps
    """
    return "<" + ",".join(list(map(lambda s: " ".join(s), xs))) + ">"

def equalAmodB(base,a,b):
    """
    The symbol numbered (base+1) must occur a number of times
    equivalent to a modulo b.
    """
    x = symbols[base]
    cycle = "*%||%<" + " ".join(b*[x]) + ">"
    prefix = "%||%<" + " ".join((a%b)*[x]) + ">"
    if (a%b) == 0:
        return "[%s]%s" % (x,cycle)
    return "[%s]@(%s,%s)" % (x,prefix,cycle)

def lessEqAmodB(base,a,b):
    """
    The symbol numbered (base+1) must occur a number of times
    less than or equal to a modulo b.
    """
    x = symbols[base]
    cycle = "*%||%<" + " ".join(b*[x]) + ">"
    prefix = "%||%<" + " ".join((a%b)*[x]) + ">"
    if (a%b) == 0:
        return "[%s]%s" % (x,cycle)
    return "[%s]@($%s,%s)" % (x,prefix,cycle)

def parityFlipShort(base):
    """
    Require an occurrence of the first symbol (a)
    not ever followed by a subsequence of the remaining symbols
    up to (base) in order.
    """
    pos = "|%<" + " ".join(symbols[:1]) + ">"
    neg = "<" + " ".join(symbols[1:base]) + ">"
    return "@(%s,~%s)" % (pos,neg)

def parityFlipLong(base):
    """
    Require a subsequence consisting of the first (base-1) symbols
    in order, not ever followed by the symbol numbered base.
    """
    pos = "|%<" + " ".join(symbols[:(base-1)]) + ">"
    neg = "<" + " ".join(symbols[(base-1):base]) + ">"
    return "@(%s,~%s)" % (pos,neg)

def dxbb2(base):
    """
    The language BB2=(a(ab)*b)* of Krebs et al (2020)
    extended in two ways:
    1) it is prepended by . (as in, a singular occurrence of any symbol)
    2) it is unioned with other symbol pairs up to (base)
       e.g. (c(cd)*d)* etc
    """
    nonempty="~%||%<>"
    dot=intersection(nonempty,"~"+leastn(2,nonempty))
    a=[]
    for i in range(0,base,2):
        x = "%||%<" + symbols[i] + ">"
        y = "%||%<" + symbols[i+1] + ">"
        xystar = "*%||%<" + symbols[i] + " " + symbols[i+1] + ">"
        a.append("@(%s,*@(%s,%s,%s))" % (dot,x,xystar,y))
    return union(*a)

def main():
    """
    write files representing constraints
    """
    for sigma in [4, 16, 64]:
        f=open("%s/syms%02d.plebby" % (dir, sigma), "w")
        f.write(symbolDefs(sigma) + "\n")
        f.close()
        base = sigma.bit_length()-1

        # Prime Cyclic Groups: Zp
        writeFile(sigma,sigma,"Zp",2,1,0,equalAmodB(base,0,2))
        writeFile(sigma,sigma,"Zp",2,1,1,equalAmodB(base,1,2))
        writeFile(sigma,sigma,"Zp",3,1,2,equalAmodB(base,0,3))
        writeFile(sigma,sigma,"Zp",3,1,3,equalAmodB(base,1,3))
        writeFile(sigma,sigma,"Zp",3,1,4,equalAmodB(base,2,3))
        writeFile(sigma,sigma,"Zp",3,1,5,"~"+equalAmodB(base,0,3))
        writeFile(sigma,sigma,"Zp",3,1,6,"~"+equalAmodB(base,1,3))
        writeFile(sigma,sigma,"Zp",3,1,7,"~"+equalAmodB(base,2,3))
        writeFile(sigma,sigma,"Zp",5,1,8,equalAmodB(base,0,5))
        writeFile(sigma,sigma,"Zp",5,1,9,lessEqAmodB(base,2,5))
        
        # Star-Free
        sf3=("@(|%<" + symbols[base] + ">,"
             + gapAlt(2,2,base)
             + ",%|<" + symbols[base] + ">)")
        writeFile(sigma,sigma,"SF",0,0,0,parityFlipShort(base+1))
        writeFile(sigma,sigma,"SF",0,0,1,parityFlipLong(base+1))
        writeFile(sigma,sigma,"SF",0,0,2,dxbb2(base))
        writeFile(sigma,sigma,"SF",0,0,3,sf3)
        writeFile(sigma,sigma,"SF",0,0,4,union(dxbb2(2),sf3))
        writeFile(sigma,sigma,"SF",0,0,5,
                  boundaryCondition(parityFlipShort(base+1),2))
        writeFile(sigma,sigma,"SF",0,0,6,
                  boundaryCondition(parityFlipLong(base+1),2))
        writeFile(sigma,sigma,"SF",0,0,7,
                  boundaryCondition(dxbb2(base),2))
        writeFile(sigma,sigma,"SF",0,0,8,
                  boundaryCondition(sf3,2))
        writeFile(sigma,sigma,"SF",0,0,9,
                  boundaryCondition(union(dxbb2(2),sf3),2))

        # Regular: even-x along with something from each other class
        evenX = equalAmodB(base,0,2)
        writeFile(sigma,sigma,"Reg",0,0,0,
                  intersection(evenX, halfAlternation(base,2," "))) # SL
        writeFile(sigma,sigma,"Reg",0,0,1,
                  intersection(evenX,
                               tierify(sigma,base+1,
                                       halfAlternation(base,2," ")))) # TSL
        writeFile(sigma,sigma,"Reg",0,0,2,
                  intersection(evenX, halfAlternation(base,2,","))) # SP
        writeFile(sigma,sigma,"Reg",0,0,3,
                  intersection(evenX,
                               union(fullAlternation(1,2," "),
                                     universalOCP(base,2," ")))) # LT
        writeFile(sigma,sigma,"Reg",0,0,4,
                  intersection(
                      evenX,
                      tierify(sigma,base,
                              union(fullAlternation(1,2," "),
                                    universalOCP(base,2," "))))) # TLT
        writeFile(sigma,sigma,"Reg",0,0,5,
                  intersection(evenX,
                               union(fullAlternation(1,2,","),
                                     universalOCP(base,2,",")))) # PT
        writeFile(sigma,sigma,"Reg",0,0,6,
                  intersection(evenX,leastn(3,altk(base,2)))) # LTT (no TLTT)
        writeFile(sigma,sigma,"Reg",0,0,7,
                  intersection(evenX,gapAlt(base,2))) # LPT
        writeFile(sigma,sigma,"Reg",0,0,8,
                  intersection(evenX,
                               tierify(sigma,base,
                                       gapAlt(base,2)))) # TLPT
        writeFile(sigma,sigma,"Reg",0,0,9,
                  intersection(evenX,union(dxbb2(2),sf3))) # SF

        for tau in [sigma, base, 2*base-1]:
            for k in [2, 4, 6]:
                # (Tier-Based) Strictly Local
                writeFile(sigma,tau,"SL",k,1,0,universalOCP(1,k," "))
                writeFile(sigma,tau,"SL",k,1,1,halfAlternation(base,k," "))
                writeFile(sigma,tau,"SL",k,1,2,fullAlternation(1,k," "))
                writeFile(sigma,tau,"SL",k,1,3,universalOCP(base,k," "))
                writeFile(sigma,tau,"SL",k,1,4,
                          boundaryCondition(universalOCP(1,k," "),k))
                writeFile(sigma,tau,"SL",k,1,5,
                          boundaryCondition(halfAlternation(base,k," "),k))
                writeFile(sigma,tau,"SL",k,1,6,
                          boundaryCondition(fullAlternation(1,k," "),k))
                writeFile(sigma,tau,"SL",k,1,7,
                          boundaryCondition(universalOCP(base,k," "),k))
                writeFile(sigma,tau,"SL",k,1,8,
                          boundaryCondition(notEndA(k, " "),k))
                writeFile(sigma,tau,"SL",k,1,9,
                          boundaryCondition(endB(k, " "),k))

                # Strictly Piecewise
                writeFile(sigma,tau,"SP",k,1,0,universalOCP(1,k,","))
                writeFile(sigma,tau,"SP",k,1,1,halfAlternation(base,k,","))
                writeFile(sigma,tau,"SP",k,1,2,fullAlternation(1,k,","))
                writeFile(sigma,tau,"SP",k,1,3,universalOCP(base,k,","))
                writeFile(sigma,tau,"SP",k,1,4,
                          boundaryCondition(universalOCP(1,k,","),k,","))
                writeFile(sigma,tau,"SP",k,1,5,
                          boundaryCondition(halfAlternation(base,k,","),k,","))
                writeFile(sigma,tau,"SP",k,1,6,
                          boundaryCondition(fullAlternation(1,k,","),k,","))
                writeFile(sigma,tau,"SP",k,1,7,
                          boundaryCondition(universalOCP(base,k,","),k,","))
                writeFile(sigma,tau,"SP",k,1,8,
                          boundaryCondition(notEndA(k, ","),k,","))
                writeFile(sigma,tau,"SP",k,1,9,
                          boundaryCondition(endB(k, ","),k,","))

                # (Tier-Based) Locally Testable
                writeFile(sigma,tau,"LT",k,1,0,
                          implication("~"+universalOCP(1,k," "),
                                      "~"+halfAlternation(1,k," ")))
                writeFile(sigma,tau,"LT",k,1,1,
                          implication("~"+universalOCP(1,k," "),
                                      "~"+halfAlternation(base,k," ")))
                writeFile(sigma,tau,"LT",k,1,2,
                          union(fullAlternation(1,k," "),
                                universalOCP(base,k," ")))
                writeFile(sigma,tau,"LT",k,1,3,
                          implication(fullAlternation(1,k," "),
                                      universalOCP(base,k," ")))
                writeFile(sigma,tau,"LT",k,1,4,
                          "~"+biimplication(universalOCP(1,k," "),
                                            fullAlternation(1,k," ")))
                writeFile(sigma,tau,"LT",k,1,5,
                          boundaryCondition(
                              implication("~"+universalOCP(1,k," "),
                                          "~"+halfAlternation(1,k," ")),
                              k," "))
                writeFile(sigma,tau,"LT",k,1,6,
                          boundaryCondition(
                              implication("~"+universalOCP(1,k," "),
                                          "~"+halfAlternation(base,k," ")),
                              k," "))
                writeFile(sigma,tau,"LT",k,1,7,
                          boundaryCondition(
                              union(fullAlternation(1,k," "),
                                    universalOCP(base,k," ")),
                              k," "))
                writeFile(sigma,tau,"LT",k,1,8,
                          boundaryCondition(
                              implication(fullAlternation(1,k," "),
                                          universalOCP(base,k," ")),
                              k," "))
                writeFile(sigma,tau,"LT",k,1,9,
                          boundaryCondition(
                              "~"+biimplication(universalOCP(1,k," "),
                                                fullAlternation(1,k," ")),
                              k," "))

                # Piecewise Testable
                writeFile(sigma,tau,"PT",k,1,0,
                          implication("~"+universalOCP(1,k,","),
                                      "~"+halfAlternation(1,k,",")))
                writeFile(sigma,tau,"PT",k,1,1,
                          implication("~"+universalOCP(1,k,","),
                                      "~"+halfAlternation(base,k,",")))
                writeFile(sigma,tau,"PT",k,1,2,
                          union(fullAlternation(1,k,","),
                                universalOCP(base,k,",")))
                writeFile(sigma,tau,"PT",k,1,3,
                          implication(fullAlternation(1,k,","),
                                      universalOCP(base,k,",")))
                writeFile(sigma,tau,"PT",k,1,4,
                          "~"+biimplication(universalOCP(1,k,","),
                                            fullAlternation(1,k,",")))
                writeFile(sigma,tau,"PT",k,1,5,
                          boundaryCondition(
                              implication("~"+universalOCP(1,k,","),
                                          "~"+halfAlternation(1,k,",")),
                              k,","))
                writeFile(sigma,tau,"PT",k,1,6,
                          boundaryCondition(
                              implication("~"+universalOCP(1,k,","),
                                          "~"+halfAlternation(base,k,",")),
                              k,","))
                writeFile(sigma,tau,"PT",k,1,7,
                          boundaryCondition(
                              union(fullAlternation(1,k,","),
                                    universalOCP(base,k,",")),
                              k,","))
                writeFile(sigma,tau,"PT",k,1,8,
                          boundaryCondition(
                              implication(fullAlternation(1,k,","),
                                          universalOCP(base,k,",")),
                              k,","))
                writeFile(sigma,tau,"PT",k,1,9,
                          boundaryCondition(
                              "~"+biimplication(universalOCP(1,k,","),
                                                fullAlternation(1,k,",")),
                              k,","))

                # (Tier-Based) Locally Threshold Testable
                for t in [2,3,5]:
                    if (k == 6 and t != 2) or (k != 2 and t == 5):
                        continue
                    writeFile(sigma,tau,"LTT",k,t,0,
                              leastn(t,ak(k)))
                    writeFile(sigma,tau,"LTT",k,t,1,
                              "~"+leastn(t,altk(base,k)))
                    writeFile(sigma,tau,"LTT",k,t,2,
                              leastnOr1(t,ak(k)))
                    writeFile(sigma,tau,"LTT",k,t,3,
                              leastnOr1(t,altk(2,k)))
                    writeFile(sigma,tau,"LTT",k,t,4,
                              intersection(leastn(t,ak(k)),
                                           "~"+leastn(t,altk(2,k))))
                    writeFile(sigma,tau,"LTT",k,t,5,
                              boundaryCondition(leastn(t,ak(k)),k))
                    writeFile(sigma,tau,"LTT",k,t,6,
                              boundaryCondition("~"+leastn(t,altk(base,k)),k))
                    writeFile(sigma,tau,"LTT",k,t,7,
                              boundaryCondition(leastnOr1(t,ak(k)),k))
                    writeFile(sigma,tau,"LTT",k,t,8,
                              boundaryCondition(leastnOr1(t,altk(2,k)),k))
                    writeFile(sigma,tau,"LTT",k,t,9,
                              boundaryCondition(
                                  intersection(leastn(t,ak(k)),
                                               "~"+leastn(t,altk(2,k))),k))

                # (Tier-Based) Locally Piecewise-Testable
                j = 2
                if (k == 6):
                    j = 3
                a = symbols[0]
                b = symbols[1]
                c = symbols[2]
                d = symbols[3]
                if (base < 4):
                    c = a
                    d = b
                writeFile(sigma,tau,"LP",k,j,0,
                          gapAlt(2,2,j))
                writeFile(sigma,tau,"LP",k,j,1,
                          "~"+lp((j*[[b], [a,a]])[:j+1]))
                writeFile(sigma,tau,"LP",k,j,2,
                          lp(j*[[a,a]]))
                writeFile(sigma,tau,"LP",k,j,3,
                          lp((j*[[a,b],[c,d]])[:j]))
                writeFile(sigma,tau,"LP",k,j,4,
                          implication(
                              lp((j*[[a,b],[b,a]])[:j]),
                              lp(([[b,a]]+j*[[a,b]])[:j])))
                writeFile(sigma,tau,"LP",k,j,0,
                          boundaryCondition(gapAlt(2,2,j),1))
                writeFile(sigma,tau,"LP",k,j,1,
                          boundaryCondition(
                              "~"+lp((j*[[b], [a,a]])[:j+1]),1))
                writeFile(sigma,tau,"LP",k,j,2,
                          boundaryCondition(
                              lp(j*[[a,a]]),1))
                writeFile(sigma,tau,"LP",k,j,3,
                          boundaryCondition(
                              lp((j*[[a,b],[c,d]])[:j]),1))
                writeFile(sigma,tau,"LP",k,j,4,
                          boundaryCondition(
                              implication(
                                  lp((j*[[a,b],[b,a]])[:j]),
                                  lp(([[b,a]]+j*[[a,b]])[:j])),1))

if __name__ == "__main__":
    main()
