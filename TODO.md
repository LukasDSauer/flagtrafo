### TODOS:


## Features and stability:

* Handling lines at infinity.
 --> Seems alright to me. The browser simply doesn't depict anything when the line is at infinity. Could
     the error message in the browser console be a problem anyway?

* Adding licences to alien software parts.

* Shear flow: Unusal orderings of the tuple: 0,2, 1, 3.
 Is the behaviour reasonable or not.
 
* Correct middle triangle for case n = 4

* Ellipse for case n = 4 and shear flow

* Convex set for cases up to n = 10.


## Ansible install:

* Which files do I need on the install side?
    * ansible-playbook
* Which files do I need on the server?
    * python3
    * pip3
* What we can remove again from the server?
    * virtualenv
    * (ansible?)
    * ansible-playbook