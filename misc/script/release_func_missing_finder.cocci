@e11 exists@
expression nm;
expression E != {0};
statement S;
position p1, p2;
identifier alloc, release;
@@
 nm = alloc(...);
 if (nm == NULL) S
   ... when != release(nm)
       when forall
 if@p1 (...) {
   ... when != release(nm)
       when forall
   release(nm);
   ... when != release(nm)
       when forall
   return@p2 E;
  }

@e12 depends on e11@
type T;
identifier e11.alloc;
@@
static T alloc(...)
{
  ...
}

@e21 exists@
expression ret, nm;
expression E != {0};
statement S;
position p1, p2;
identifier alloc, release;
@@
 ret = alloc(nm);
 if (\(ret < 0\|ret != 0\)) S
   ... when != release(nm)
 if@p1 (...) {
   ... when != release(nm)
       when forall
   release(nm);
   ... when != release(nm)
       when forall
   return@p2 E;
  }

@e22 depends on e21@
type T;
identifier e21.alloc;
@@
static T alloc(...)
{
  ...
}

@script:python depends on e11 && !e12@
alloc << e11.alloc;
release << e11.release;
@@
_skiplist = ['kzalloc', 'kmalloc', 'ioremap', 'pci_enable_device']
if alloc.find('devm_') != 0 and _skiplist.count(alloc) == 0:
    print "%s|%s|1" % (alloc, release)

@script:python depends on e21 && !e22@
alloc << e21.alloc;
release << e21.release;
@@
_skiplist_a = ['kzalloc', 'kmalloc', 'ioremap', 'pci_enable_device']
_skiplist_r = ['kfree']

if alloc.find('devm_') != 0 and _skiplist_a.count(alloc) == 0 and _skiplist_r.count(release) == 0:
    print "%s|%s|2" % (alloc, release)
