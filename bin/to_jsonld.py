import json
import sys
import os
from liquix_export.settings import NAMESPACE

def obj_uri(kind, id):
    return "{}{}/{}".format(NAMESPACE, kind, id)


def map_av(x):
    x["@type"] = "AromaVendor"
    return x


def map_a(x):
    x["@type"] = "Aroma"
    x["@id"] = obj_uri("Aroma", x['id'])
    return x


def map_base(x):
    x["@type"] = "Base"
    x["@id"] = obj_uri("Base", x['id'])
    return x


def map_fav(x):
    x["@type"] = "Favorite"
    return x


def map_recipe(x):
    def map_comp((uri, perc)):
        return {
            "@type": "RecipeCompenent",
            "ingredient": uri,
            "percentage": perc
        }

    x["@type"] = "Recipe"
    x["@id"] = obj_uri("Recipe", x["caption"])
    x["components"] = map(
        map_comp,
        zip(
            map(lambda x: obj_uri("Aroma", x), x['aromasID']),
            x['aromasTargetPerc']
        ) 
    )


    x["basePG"] = obj_uri("Base", x["basePG"])
    x["baseVG"] = obj_uri("Base", x["baseVG"])
    x["base"] = obj_uri("Base", x["base"])

    del x["aromasID"]
    del x["aromasTargetPerc"]

    return x


def jsonld_wrap(items):
    return {
        "@graph": items,
        "@context": {
            "@vocab": NAMESPACE,
            "ingredient": {"@type": "@id"},
            "base": {"@type": "@id"},
            "baseVG": {"@type": "@id"},
            "basePG": {"@type": "@id"},
        }
    }


def map_graph(mapper, jsonld):
    jsonld["@graph"] = map(mapper, jsonld["@graph"])
    return jsonld


def merge_graphs(*jsonlds):
    data = jsonld_wrap([])
    for jsonld in jsonlds:
        data["@graph"] += jsonld["@graph"]
    return data


def main(root):
    def load(filename):
        return jsonld_wrap(
            json.load(open(os.path.join(root, filename)))
        )


    avs = map_graph(map_av, 
                    load("List_AromaVendors.json"))

    aromas = map_graph(map_a, 
                       load("List_Aromas.json"))

    bases = map_graph(map_base, 
                      load("List_Bases.json"))

    favs = map_graph(map_fav, 
                     load("List_Favorites.json"))

    recipes = map_graph(map_recipe, 
                        load("List_Recipes.json"))


    data = merge_graphs(
#        avs,
        aromas,
        bases,
#        favs,
        recipes
    )
    data['items'] = data['@graph']
    del data['@graph']
    json.dump(data, sys.stdout, indent=2)

if __name__ == '__main__':
    main(sys.argv[1])
