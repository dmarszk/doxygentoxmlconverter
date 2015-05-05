A very very quickly and badly written converter between Doxygen and XML source code documentation.

In essence, transforming:
```
            /**
             * @brief Transform a floating-point vector by the properties passed to the class.
             * @param vVector The vector to transform.
             */
            public void transformVector(ref Vector3 vVector)
```
into:
```
            /// <summary>
            /// Transform a floating-point vector by the properties passed to the class.
            /// </summary>
            /// <param name="vVector">The vector to transform.</param>
            public void transformVector(ref Vector3 vVector)
```
I would like to add that this is far from my finest code and that it is only here because I could not see anything else like it out there.  Please use it and contribute changes back in the same spirit. :-)