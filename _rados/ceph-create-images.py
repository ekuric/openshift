import rados
import rbd
import argparse

__author__ = "Elko"

"""
script to create ceph pool - if not exist, and crate desired set of images
on top of with desired size
"""

def main():

    # parse arguments
    parser = argparse.ArgumentParser(description="script to create ceph images of sepcified size")
    parser.add_argument("-p","--pname", help="pool name", type=str)
    parser.add_argument("-n", "--nimages", help="number of images on pool", type=int)
    parser.add_argument("-s", "--size", help="size of images", type=int)
    parser.add_argument("-i", "--iname", help="prefix for image name" , type=str)

    args = parser.parse_args()

    pname = args.pname
    nimages = args.nimages
    isize = args.size * 1024**3
    iname = args.iname

    # create ceph cluster handle
    # defaults : user=admin, conffile=/etc/ceph/ceph.conf
    try:
        cluster = rados.Rados(conffile="/etc/ceph/ceph.conf")
        cluster.connect()
    except Exception as e:
        print ("Not possible to connect to ceph cluster")
        raise
    print ("Connected")

    def get_create_pool():
        """ Create pool if it does not exits  """
        # check http://docs.ceph.com/docs/master/rbd/librbdpy/
        if pname not in cluster.list_pools():
            cluster.create_pool(pname)
        else:
            print ("pool", pname,  "exist, we are not going to re-create it")
        return pname

    def create_images():
        """  Create desired number of images - these will be used by pods  """
        createdimages = 0
        iocntx = cluster.open_ioctx(pname)
        rbd_ins = rbd.RBD()
        while createdimages < nimages:
            rbd_ins.create(iocntx, str(iname) + str(createdimages), isize)
            createdimages = createdimages + 1

    # run functions

    get_create_pool()
    create_images()


#  main

if __name__ == "__main__":
    main()


