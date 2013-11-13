@ty1@
identifier I, nm, fld;
@@
const struct I nm = {
...,
.fld = THIS_MODULE,
...
};

@script:python depends on ty1@
fld << ty1.fld;
I << ty1.I;
@@

print "%s|%s" % (I, fld)

