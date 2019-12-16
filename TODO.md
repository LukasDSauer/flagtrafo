### TODOS:


## Features and stability:

* Handling lines at infinity.
 --> Seems alright to me. The browser simply doesn't depict anything when the line is at infinity. Could
     the error message in the browser console be a problem anyway?

* Adding licences to alien software parts.

* Shear flow: Unusal orderings of the tuple: 0,2, 1, 3.
 Is the behaviour reasonable or not.
 
* Correct middle triangle for case n = 4 --> Done!

* Ellipse for case n = 4 and shear flow --> Done!

* Eruption flow for case n=4.

* Convex set for cases n > 4. --> Done!

* Problem: Shear flow is an option for n=3.


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