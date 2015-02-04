from rdflib import Graph, Namespace, Literal
from liquix_export.settings import NAMESPACE
import sys
from tabulate import tabulate
import re


ns = Namespace(NAMESPACE)

def query_components(g, name):
    return [
        (r.comp_name.toPython(), r.percent.toPython())
        for r in
        g.query(
            """
            SELECT *
            WHERE {
              ?obj l:caption ?name ;
                   l:components ?comp .

              ?comp l:ingredient ?ingredient ;
                    l:percentage ?percent .

              ?ingredient l:caption ?comp_name 
            }
            """,
            initBindings={"name": Literal(name)}
        )
    ]


def all_names(g):
    return [
        r.name 
        for r in g.query(
                """
                SELECT ?name WHERE {
                  ?obj l:caption ?name ;
                       a l:Recipe .
                }
                """
        )
    ]


def main(regex):
    g = Graph().parse(sys.stdin, format="json-ld")
    g.namespace_manager.bind("l", NAMESPACE)

    names = [
        name
        for name in all_names(g)
        if regex.match(name) is not None
    ]
            
    for name in names:
        components = query_components(g, name)
        print "="*79
        print name
        print "="*79
        print
        print tabulate(
            components,
            headers=["flavor", "percentage"]
        )
        print

if __name__ == '__main__':
    main(re.compile(sys.argv[1]))
