/// using kfree_rcu() to simplify the code
///
/// The callback function of call_rcu() just calls a kfree(), so we
/// can use kfree_rcu() instead of call_rcu() + callback function.
/// 
/// dpatch engine is used to auto generate this patch.
/// (https://github.com/weiyj/dpatch)
///
@r1@
type T;
identifier fn;
identifier info, head, rcu;
@@
void fn(struct rcu_head *head)
{
	T *info;
	info = container_of(head, T, rcu);
	kfree(info);
}

@p11 depends on r1@
identifier r1.fn;
identifier r1.rcu;
identifier info;
@@

- call_rcu(&info->rcu, fn);
+ kfree_rcu(info, rcu);

@p12 depends on p11 && r1@
type r1.T;
identifier r1.fn;
identifier r1.info, r1.head, r1.rcu;
@@
- void fn(struct rcu_head *head)
- {
- 	T *info;
- 	info = container_of(head, T, rcu);
- 	kfree(info);
- }

@r2@
type T;
identifier fn;
identifier info, head, rcu;
@@
void fn(struct rcu_head *head)
{
	T *info = container_of(head, T, rcu);
	kfree(info);
}

@p21 depends on r2@
identifier r2.fn;
identifier r2.rcu;
identifier info;
@@

- call_rcu(&info->rcu, fn);
+ kfree_rcu(info, rcu);

@p22 depends on p21 && r2@
type r2.T;
identifier r2.fn;
identifier r2.info, r2.head, r2.rcu;
@@
- void fn(struct rcu_head *head)
- {
- 	T *info = container_of(head, T, rcu);
- 	kfree(info);
- }

@r3@
type T;
identifier fn;
identifier head, rcu;
@@
void fn(struct rcu_head *head)
{
	kfree(container_of(head, T, rcu));
}

@p31 depends on r3@
identifier r3.fn;
identifier r3.rcu;
identifier info;
@@

- call_rcu(&info->rcu, fn);
+ kfree_rcu(info, rcu);

@p32 depends on p31 && r3@
type r3.T;
identifier r3.fn;
identifier r3.head, r3.rcu;
@@
- void fn(struct rcu_head *head)
- {
- 	kfree(container_of(head, T, rcu));
- }
