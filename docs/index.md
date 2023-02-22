
As geodesists that use the Bernese GNSS Software [BSW] for different campaign
types, we need a software system that automates the creation of campaigns,
downloads necessary data, configures and starts BSW's processing engine [BPE],
and, finally, assures the quality of and handles the end products that come out
of the BPE process.


## User interface design | In development

!!! warning "Under development"

    The UI design is under development and the following is more like a lorem-ipsum
    text for the documentation.

Ideas:

```
ab campaign create --type nkg --name nkg2222
ab campaign run nkg2222
ab data update --all
```


```
# Download af data til indplacering i filstruktur på KMSFS8.
ab download-data <TIDSPUNKT> <DATATYPE> <DATATYPE> ... <DATATYPE>

# Oprettelse af ny station, fx opdatering STA-fil og beregning af foreløbige koordinater
ab ny-station <STATION>

# Pendant til Søren Juels NKG-scripts
ab regn-kampagne <NGK|5D|KDI> --stationer ABCD,EFGH,...,ZXYZ

```

## References

*   [Agency for Data Supply and Infrastructure](https://eng.sdfi.dk/)
*   [Bernese GNSS Software](http://www.bernese.unibe.ch/)
