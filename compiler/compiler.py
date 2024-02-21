import os
import json
import shutil
import subprocess


def get_vanilla_items():
    with open("resources/item_orders/wiki_order.json", "r") as f:
        return json.loads(f.read())["order"]


class Compiler:
    vanilla_items = get_vanilla_items()


    def __init__(self, current_project):
        self.current_project = current_project

        with open(f"{self.current_project}/properties.json", "r") as f:
            self.properties = json.loads(f.read())

        self.domain = "net.minecraftmoddingtool." + self.properties["mod_id"]
        self.translations = {}
        self.items = []
        self.blocks = []
        self.fence_blocks = []
        self.fence_gate_blocks = []
        self.wall_blocks = []
        self.door_blocks = []
        self.trapdoor_blocks = []

        self.mod_items = []

    def compile(self):
        self.copy_files()
        self.initialize_mod_items_variable()
        self.initialize_gradle_properties()
        self.initialize_mod_items()
        self.initialize_mod_item_groups()
        self.initialize_mod_main()
        self.initialize_fabric_mixins()
        self.initialize_fabric_mod()
        self.initialize_mod_blocks()
        self.initialize_mod_model_provider()
        self.initialize_mod_recipe_provider()
        self.initialize_mod_recipe_provider_smelting()
        self.initialize_self_drops()
        self.initialize_mineable_tags()
        self.initialize_block_type_tags()
        self.initialize_food_components()
        self.initialize_fuel_items()
        self.initialize_mod_client()
        self.initialize_textures()
        self.initialize_translations()

    def copy_files(self):
        if os.path.isdir(os.path.join(self.current_project, "compiled")):
            shutil.rmtree(os.path.join(self.current_project, "compiled"))

        shutil.copytree("templates/files", f"{self.current_project}/compiled")
        cur_domain = ""
        for folder in self.domain.split(".")[:-1]:
            cur_domain += folder
            os.mkdir(os.path.join(self.current_project, "compiled", "src", "main", "java", cur_domain))
            cur_domain += "/"
        shutil.copytree("templates/javaSRC", os.path.join(self.current_project, "compiled", "src", "main", "java", cur_domain, self.properties["mod_id"]))

        shutil.copytree("templates/assets/dummy", os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"]))

    def initialize_mod_items_variable(self):
        for path in os.listdir(os.path.join(self.current_project, "items")):
            with open(os.path.join(self.current_project, "items", path)) as f:
                self.mod_items.append(json.loads(f.read())["id"])

    def initialize_gradle_properties(self):
        contents = ""
        gradle_file = os.path.join(self.current_project, "compiled", "gradle.properties")
        with open(gradle_file, "r") as f:
            contents = str(f.read())
        contents = Compiler.bulk_replace(contents, {"%modVersion%": "0.1", f"%domain%": self.domain, "%modID%": self.properties["mod_id"]})
        print(contents)

        with open(gradle_file, "w") as f:
            f.write(contents)

    def initialize_mod_items(self):
        imports, content = Compiler.parse_template("templates/snippets/item_adder.txt")

        combined_contents = ""

        for path in os.listdir(os.path.join(self.current_project, "items")):
            with open(os.path.join(self.current_project, "items", path), "r") as f:
                self.items.append(json.loads(f.read()))

        for item in self.items:
            self.translations["item." + ".".join(item["id"].split(":"))] = item["name"]

            food_code = ""
            if "foodProperties" in item.keys():
                food_code = f".food(ModFoodComponents.{item['id'].split(':')[1].upper()})"

            contents_copy = content[:]
            contents_copy = Compiler.bulk_replace(contents_copy, {f"%itemVar%": item["id"].split(":")[1].upper(), f"%itemID%": item["id"].split(":")[1],
            f"%food%": food_code})
            combined_contents += contents_copy + "\n"

        contents = ""
        with open(os.path.join(self.current_project, "compiled", "src", "main", "java", *self.domain.split("."), "item", "ModItems.java"), "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%imports%": imports, f"%registerItems%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_item_groups(self):
        contents = ""
        imports, content = Compiler.parse_template("templates/snippets/item_group_adder.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""

        item_groups = []
        for path in os.listdir(os.path.join(self.current_project, "item_groups")):
            with open(os.path.join(self.current_project, "item_groups", path), "r") as f:
                item_groups.append(json.loads(f.read()))
        
        for group in item_groups:
            content_copy = content[:]

            icon = group["icon"]
            group_items = group["items"]
            if icon.startswith("minecraft:"):
                iconItem = "Items." + icon.split(":")[1].upper()
            else:
                iconItem = "ModItems." + icon.split(":")[1].upper()

            content_copy = Compiler.bulk_replace(content_copy, {f"%GROUP_NAME%": group["id"].upper(), f"%groupID%": group["id"], 
            f"%modID%": self.properties["mod_id"], f"%iconItem%": iconItem, f"%Items%": self.get_item_to_item_group_code(group_items)})
            combined_contents += content_copy + "\n"
            self.translations["itemgroup." + group["id"]] = group["name"]

        contents = ""
        with open(os.path.join(self.current_project, "compiled", "src", "main", "java", *self.domain.split("."), "item", "ModItemGroups.java"), "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%imports%": imports, f"%insertItemGroups%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_main(self):
        for path in ["ModMain.java", "ModClient.java", "ModDataGenerator.java"]:
            with open(os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), path), "r+") as f:
                contents = f.read()
                contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, "%modID%": self.properties["mod_id"]})
                f.seek(0)
                f.truncate(0)
                f.write(contents)

    def initialize_fabric_mixins(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/resources/")
        os.rename(os.path.join(resource_path, "dummy.mixins.json"), os.path.join(resource_path, f"{self.properties['mod_id']}.mixins.json"))
        
        with open(os.path.join(resource_path, f"{self.properties['mod_id']}.mixins.json"), "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%mixins%": ""})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_fabric_mod(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/resources/fabric.mod.json")

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%modID%": self.properties["mod_id"], f"%modName%": self.properties["title"],
            f"%modDescr%": "A Mod Created with MinecraftModdingTool!", f"%domain%": self.domain})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_blocks(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "block/ModBlocks.java")
        imports, content = Compiler.parse_template("templates/snippets/block_adder.txt")
        imports_exp, content_exp = Compiler.parse_template("templates/snippets/experience_block_adder.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for path in os.listdir(os.path.join(self.current_project, "blocks")):
            with open(os.path.join(self.current_project, "blocks", path), "r") as f:
                self.blocks.append(json.loads(f.read()))

        for block in self.blocks:
            content_copy = content[:]
            if "blockType" in block.keys():
                with open(os.path.join(self.current_project, "blocks", block["blockModel"].split(":")[1] + ".json"), "r") as f:
                    modelBlock = json.loads(f.read())
                    block["properties"] = modelBlock["properties"]
                if block["blockType"] == "Stairs":
                    argsBefore = f"ModBlocks.{block['blockModel'].split(':')[1].upper()}.getDefaultState(), "
                    argsAfter = ""
                elif block["blockType"] == "Button":
                    argsBefore = ""
                    argsAfter = f".collidable(false), BlockSetType.IRON, {block['pressTime']}, {str(block['arrowTriggerable']).lower()}"
                elif block["blockType"] == "Pressure Plate":
                    argsBefore = f"PressurePlateBlock.ActivationRule.{'EVERYTHING' if block['itemTriggerable'] else 'MOBS'}, "
                    argsAfter = f", BlockSetType.IRON"
                elif block["blockType"] == "Fence Gate":
                    argsBefore = ""
                    argsAfter = f", WoodType.ACACIA"
                elif block["blockType"] == "Door":
                    argsBefore = ""
                    argsAfter = f".nonOpaque(), BlockSetType.{'CHERRY' if block['handOpenableDoor'] else 'IRON'}"
                elif block["blockType"]  == "Trapdoor":
                    argsBefore = ""
                    argsAfter = f".nonOpaque(), BlockSetType.{'CHERRY' if block['handOpenableTrapdoor'] else 'IRON'}"
                else:
                    argsBefore = argsAfter = ""

                if block["blockType"] == "Fence":
                    self.fence_blocks.append(block)
                elif block["blockType"] == "Fence Gate":
                    self.fence_gate_blocks.append(block)
                elif block["blockType"] == "Wall":
                    self.wall_blocks.append(block)
                elif block["blockType"] == "Door":
                    self.door_blocks.append(block)
                elif block["blockType"] == "Trapdoor":
                    self.trapdoor_blocks.append(block)
            else: 
                argsBefore = argsAfter = ""  
                block["blockType"] = ""

            replacements = {
                f"%blockVar%": block["id"].split(":")[1].upper(),
                f"%handBreakable%": "true" if block["properties"]["handBreakable"] else "false",
                f"%breakInstantly%": ".breakInstantly()" if block["properties"]["instaminable"] else "",
                f"%requiresTool%": ".requiresTool()" if block["properties"]["requiresTool"] else "",
                f"%luminance%": f".luminance({block['properties']['lightLevel']})" if int(block["properties"]["lightLevel"]) > 0 else "",
                f"%blockID%": block["id"].split(":")[1],
                f"%strength%": f".strength({block['properties']['strength']}f)",
                f"%blockType%": "".join(block["blockType"].split()),
                f"%argsBefore%": argsBefore,
                f"%argsAfter%": argsAfter
            }

            if "drops" in block.keys() and block["drops"]["dropType"] == "Ores":
                content_copy = content_exp[:]
                replacements[f"%expLow%"] = block["drops"]["expMin"]
                replacements[f"%expHigh%"] = block["drops"]["expMax"]
            content_copy = Compiler.bulk_replace(content_copy, replacements)
            combined_contents += content_copy + "\n"

            self.translations["block." + self.properties["mod_id"] + "." + block["id"].split(":")[1]] = block["name"]
        
        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {
                f"%domain%": self.domain, "%modID%": self.properties["mod_id"], 
                f"%imports%": imports, f"%registerBlocksHere%": combined_contents
            })
            f.seek(0)
            f.truncate(0)
            f.write(contents)
    
    def initialize_mod_model_provider(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModModelProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/register_generated_model.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for item in self.items:
            content_copy = content[:]
            content_copy = Compiler.bulk_replace(content_copy, {f"%itemVar%": item["id"].split(":")[1].upper()})
            combined_contents += content_copy + "\n"

        imports2, contents2 = Compiler.parse_template("templates/snippets/register_block_cube_all_model.txt")
        imports_pool, contents_pool = Compiler.parse_template("templates/snippets/register_block_cube_with_pool.txt")
        imports_with_pool, contents_with_pool = Compiler.parse_template("templates/snippets/register_pool_model.txt")
        imports_door, contents_door = Compiler.parse_template("templates/snippets/register_door_trapdoor_model.txt")
        imports2 = Compiler.bulk_replace(imports2, {f"%domain%": self.domain})
        
        combined_contents2 = ""
        combined_contents_pooled = ""
        for block in self.blocks:
            if block["blockType"] != "":
                if block["blockType"] not in ["Trapdoor", "Door"]:
                    content_copy = contents_with_pool[:]
                    blockTypeNew = block["blockType"].split(" ")
                    blockTypeNew[0] = blockTypeNew[0].lower()
                    blockTypeNew = "".join(blockTypeNew)
                    content_copy = Compiler.bulk_replace(content_copy, {
                        f"%blockType%": blockTypeNew, 
                        f"%modelBlockVar%": block["blockModel"].split(":")[1].upper()
                    })
                    content_copy = Compiler.bulk_replace(content_copy, {f"%blockVar%": block["id"].split(":")[1].upper()})
                else:
                    content_copy = contents_door[:]
                    content_copy = Compiler.bulk_replace(content_copy, {
                        f"%blockType%": block["blockType"],
                        f"%blockVar%": self.get_space_and_var_of_item(block["id"])[1]
                    })
                combined_contents_pooled += content_copy + "\n"
            else:
                if "generatePool" not in block.keys() or not block["generatePool"]:
                    content_copy = contents2[:]
                else:
                    content_copy = contents_pool[:]
                content_copy = Compiler.bulk_replace(content_copy, {f"%blockVar%": block["id"].split(":")[1].upper()})
                combined_contents2 += content_copy + "\n"
        
        with open(resource_path, "r+") as f:
            contents = Compiler.bulk_replace(f.read(), {f"%domain%": self.domain, f"%imports%": imports, f"%itemModelsHere%": combined_contents,
            f"%blockModelsHere%": combined_contents2, f"%blockImports%": imports2, f"%blockPooledModelsHere%": combined_contents_pooled})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_recipe_provider(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModRecipeProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/shaped_recipe_adder.txt")
        imports_shapeless, content_shapeless = Compiler.parse_template("templates/snippets/shapeless_recipe_adder.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        recipes_path = os.path.join(self.current_project, "recipes")
        recipes = []
        for path in os.listdir(recipes_path):
            with open(os.path.join(recipes_path, path), "r") as f:
                recipes.append(json.loads(f.read()))

        combined_contents = ""
        for recipe in recipes:
            # Find output item
            item_space, item_var = self.get_space_and_var_of_item(recipe["outputItem"])
            output_item = item_space + "." + item_var

            if "patterns" in recipe.keys():
                # This is a shaped recipe
                content_copy = content[:]
                
                # Find Patterns
                pattern_text = ""
                for pattern in recipe["patterns"]:
                    pattern_text += f".pattern(\"{pattern}\")"
                
                # Get Keys and Criteria
                key_text = ""
                criteria_text = ""
                for key, item in recipe["key"].items():
                    ingredient_space, ingredient_var = self.get_space_and_var_of_item(item, True)
                    key_text += f".input('{key}', {ingredient_space}.{ingredient_var})"

                    criteria_text += f".criterion(hasItem({ingredient_space}.{ingredient_var}), conditionsFromItem({ingredient_space}.{ingredient_var}))"
                

                content_copy = Compiler.bulk_replace(content_copy, {
                    f"%outputItem%": output_item, 
                    f"%outputCount%": recipe["outputCount"],
                    f"%patterns%": pattern_text,
                    f"%keys%": key_text,
                    f"%criteria%": criteria_text,
                    f"%id%": recipe["id"]
                })
            else:
                # This is a shapeless recipe
                content_copy = content_shapeless[:]

                # Find inputs and criteria
                input_text = ""
                criteria_text = ""
                for item, count in recipe["inputs"].items():
                    input_space, input_var = self.get_space_and_var_of_item(item, True)
                    input_text += f".input({input_space}.{input_var}, {count})"
                    criteria_text += f".criterion(hasItem({input_space}.{input_var}), conditionsFromItem({input_space}.{input_var}))"

                content_copy = Compiler.bulk_replace(content_copy, {
                    f"%outputItem%": output_item, 
                    f"%outputCount%": recipe["outputCount"],
                    f"%inputs%": input_text,
                    f"%criteria%": criteria_text,
                    f"%id%": recipe["id"]
                })


            combined_contents += content_copy + "\n"

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%imports%": imports, f"%craftingRecipes%": combined_contents,
            f"%importsShapeless%": imports_shapeless})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_recipe_provider_smelting(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModRecipeProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/smelting_recipe_adder.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        smelting_path = os.path.join(self.current_project, "smelting")
        smelting = []
        for path in os.listdir(smelting_path):
            with open(os.path.join(smelting_path, path), "r") as f:
                smelting.append(json.loads(f.read()))

        combined_contents = ""
        i = 0
        for recipe in smelting:
            inputItemSpace, inputItemVar = self.get_space_and_var_of_item(recipe["inputItem"], True)
            itemSpace, itemVar = self.get_space_and_var_of_item(recipe["outputItem"], True)

            recipe_types = {}
            recipe_types["Smelting"] = 1
            if recipe["addBlasting"]:
                recipe_types["Blasting"] = 0.5

            for recipe_type, mult in recipe_types.items():
                replacements = {
                    f"%itemVar%": itemVar,
                    f"%itemSpace%": itemSpace,
                    f"%index%": i + 1,
                    f"%inputItemSpace%": inputItemSpace,
                    f"%inputItemVar%": inputItemVar,
                    f"%type%": recipe_type,
                    f"%experience%": float(recipe["experience"]),
                    f"%time%": int(int(recipe["smeltTime"])*mult),
                    f"%itemID%": recipe["outputItem"].split(":")[1]
                }

                content_copy = content[:]
                content_copy = Compiler.bulk_replace(content_copy, replacements)

                combined_contents += content_copy + "\n"
                i += 1            

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%importsSmelting%": imports, f"%smeltingRecipes%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)
    
    def initialize_self_drops(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModLootTableProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/register_self_drop.txt")
        imports_ore, content_ore = Compiler.parse_template("templates/snippets/add_ore_drop.txt")
        imports_door_slab, content_door_slab = Compiler.parse_template("templates/snippets/add_door_slab_drop.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for block in self.blocks:
            if block["blockType"] != "":
                if block["blockType"] not in ["Slab", "Door"]:
                    block["drops"] = {"dropType": "Self"}
                else:
                    block["drops"] = {"dropType": "SpecialBlock"}
            block_space, block_var = self.get_space_and_var_of_item(block["id"])
            replacements = {f"%itemSpace%": block_space, f"%itemVar%": block_var}
            if block["drops"]["dropType"] == "Self":
                content_copy = content[:]
            elif block["drops"]["dropType"] == "Ores":
                content_copy = content_ore[:]
                replacements[f"%dropItemSpace%"], replacements[f"%dropItemVar%"] = self.get_space_and_var_of_item(block["drops"]["droppedItem"])
                replacements[f"%min%"] = block["drops"]["itemMin"]
                replacements[f"%max%"] = block["drops"]["itemMax"]
            elif block["drops"]["dropType"] == "SpecialBlock":
                content_copy = content_door_slab[:]
                replacements[f"%blockType%"] = block["blockType"].lower()

            content_copy = Compiler.bulk_replace(content_copy, replacements)

            combined_contents += content_copy + "\n"

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%addSelfDrops%": combined_contents, f"%imports%": imports})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mineable_tags(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModBlockTagProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/register_tags.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        mineables = {"pickaxe": [], "axe": [], "shovel": [], "hoe": [], "sword": []}
        needs_tool_tier = {"stone": [], "iron": [], "diamond": [], "netherite": []}
        for block in self.blocks:
            if block["properties"]["requiredTool"] != "None":
                mineables[block["properties"]["requiredTool"].lower()].append(block)
            if block["properties"]["requiresTool"]:
                needs_tool_tier[block["properties"]["requiredTier"].lower()].append(block)


        for key, blocks in mineables.items():
            content_copy = content[:]

            if len(blocks) == 0:
                continue

            add_item_text = ""
            for block in blocks:
                add_item_text += f".add(ModBlocks.{block['id'].split(':')[1].upper()})\n"

            content_copy = Compiler.bulk_replace(content_copy, {f"%namespace%": "minecraft", "%tagName%": f"mineable/{key}",
            f"%addItems%": add_item_text})

            combined_contents += content_copy + "\n"

        for key, blocks in needs_tool_tier.items():
            content_copy = content[:]

            if len(blocks) == 0:
                continue

            add_item_text = Compiler.get_blocks_to_tag_code(blocks)

            if key == "netherite":
                content_copy = Compiler.bulk_replace(content_copy, {f"%namespace%": "fabric", f"%tagName%": "needs_tool_level_4",
                f"%addItems%": add_item_text})
            else:
                content_copy = Compiler.bulk_replace(content_copy, {f"%namespace%": "minecraft", "%tagName%": f"needs_{key}_tool",
                f"%addItems%": add_item_text})

            combined_contents += content_copy + "\n"


        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%addTags%": combined_contents, f"%imports%": imports})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_block_type_tags(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "datagen/ModBlockTagProvider.java")
        imports, content = Compiler.parse_template("templates/snippets/register_tags.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        block_types = {"fences": self.fence_blocks, "fence_gates": self.fence_gate_blocks, "walls": self.wall_blocks}
        for block_tag, block_list in block_types.items():
            content_copy = content[:]
            replacements = {
                f"%namespace%": "minecraft",
                f"%tagName%": block_tag,
                f"%addItems%": Compiler.get_blocks_to_tag_code(block_list)
            }
            combined_contents += Compiler.bulk_replace(content_copy, replacements) + "\n"

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%addSpecialBlockTags%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_food_components(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "item/ModFoodComponents.java")
        imports, content = Compiler.parse_template("templates/snippets/add_food_component.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for item in self.items:
            if "foodProperties" in item.keys():
                food_properties = item["foodProperties"]
                item_var = self.get_space_and_var_of_item(item["id"])[1]
                status_effect_code = Compiler.get_status_effect_to_food_component_code(food_properties["statusEffects"])
                
                content_copy = content[:]
                content_copy = Compiler.bulk_replace(content_copy, {f"%itemVar%": item_var, f"%hunger%": food_properties["hunger"], 
                f"%saturation%": food_properties["saturation"], f"%statusEffects%": status_effect_code, f"%alwaysEdible%": ".alwaysEdible()" if food_properties["alwaysEdible"] else ""})
                combined_contents += content_copy + "\n"
            
        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%foodComponents%": combined_contents, f"%imports%": imports})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_fuel_items(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "item/ModFuelItems.java")
        imports, content = Compiler.parse_template("templates/snippets/register_fuel_item.txt")
        imports = Compiler.bulk_replace(imports, {f"%domain%": self.domain})

        combined_contents = ""
        for item in self.items:
            if "fuelProperties" in item.keys():
                fuel_properties = item["fuelProperties"]
                item_space, item_var = self.get_space_and_var_of_item(item["id"])
    
                content_copy = content[:]
                duration = str(int(float(fuel_properties["burnItems"]) * 200))
                content_copy = Compiler.bulk_replace(content_copy, {f"%itemVar%": item_var, f"%itemSpace%": item_space, f"%duration%": duration})
                combined_contents += content_copy + "\n"
            
        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%registerFuelItems%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    def initialize_mod_client(self):
        resource_path = os.path.join(self.current_project, "compiled/src/main/java", *self.domain.split("."), "ModClient.java")
        imports, content = Compiler.parse_template("templates/snippets/add_cutout_blocks.txt")

        combined_contents = ""
        for block in [*self.door_blocks, *self.trapdoor_blocks]:
            content_copy = content[:]
            content_copy = Compiler.bulk_replace(content_copy, {
                f"%blockVar%": self.get_space_and_var_of_item(block["id"])[1]
            })
            combined_contents += content_copy + "\n"

        with open(resource_path, "r+") as f:
            contents = f.read()
            contents = Compiler.bulk_replace(contents, {f"%domain%": self.domain, f"%addCutoutBlocks%": combined_contents})
            f.seek(0)
            f.truncate(0)
            f.write(contents)

    
    def initialize_textures(self):
        for item in self.items:
            shutil.copy(item["texture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/item", item["id"].split(":")[1]+".png"))
        for block in self.blocks:
            if block["blockType"] != "":
                if block["blockType"] == "Door":
                    shutil.copy(block["bottomTexture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/block", block["id"].split(":")[1]+"_bottom.png"))
                    shutil.copy(block["topTexture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/block", block["id"].split(":")[1]+"_top.png"))
                    shutil.copy(block["itemTexture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/item", block["id"].split(":")[1]+".png"))
                elif block["blockType"] == "Trapdoor":
                    shutil.copy(block["trapdoorTexture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/block", block["id"].split(":")[1]+".png"))
            else:
                shutil.copy(block["texture"], os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "textures/block", block["id"].split(":")[1]+".png"))
    
    def initialize_translations(self):
        with open(os.path.join(self.current_project, "compiled/src/main/resources/assets/", self.properties["mod_id"], "lang/en_us.json"), "r+") as f:
            f.write(json.dumps(self.translations))

    def redo_gradle(self):
        os.chdir(os.path.join(self.current_project, "compiled"))
        subprocess.run(["./gradlew", "--daemon"])
        subprocess.run(["./gradlew", "runDatagen"])
        os.chdir("../..")

    def run_client(self):
        os.chdir(os.path.join(self.current_project, "compiled"))
        subprocess.run(["./gradlew", "runClient"])
        os.chdir("../..")
    
    @staticmethod
    def parse_template(template_file):
        imports = ""

        with open(template_file) as f:
            contents = f.read()
            imports_index = contents.find("!IMPORTS!")
            contents_index = contents.find("!CONTENT!")
            
            imports = contents[imports_index+9:contents_index].strip("\n")
            contents = contents[contents_index+9:].strip("\n")

        return imports, contents

    @staticmethod
    def bulk_replace(string, replacements):
        for src, dst in replacements.items():
            string = string.replace(src, str(dst))
        return string

    @staticmethod
    def get_status_effect_to_food_component_code(status_effects):
        imports, content = Compiler.parse_template("templates/snippets/add_status_effect_to_food.txt")

        combined_contents = ""
        for effect in status_effects:
            content_copy = content[:]
            replacements = {
                f"%effectSpace%": "StatusEffects",
                f"%effectVar%": effect["statusEffect"].split(":")[1].upper(),
                f"%duration%": effect["duration"],
                f"%amplifier%": effect["statusEffectMultiplier"],
                f"%chance%": str(min(float(effect["statusEffectChance"])/100, 1.0))
            }
            content_copy = Compiler.bulk_replace(content_copy, replacements)
            combined_contents += content_copy

        return combined_contents

    @staticmethod
    def get_blocks_to_tag_code(blocks):
        add_item_text = ""
        for block in blocks:
            add_item_text += f".add(ModBlocks.{block['id'].split(':')[1].upper()})\n"
        return add_item_text

    def get_space_and_var_of_item(self, item, ignore_vanilla_blocks=False):
        if item.startswith("minecraft:"):
            if item.split(":")[1] in Compiler.vanilla_items or ignore_vanilla_blocks:
                item_space = "Items"
            else:
                item_space = "Blocks"
        else:
            if item in self.mod_items:
                item_space = "ModItems"
            else:
                item_space = "ModBlocks"
        return item_space, item.split(":")[1].upper()

    def get_item_to_item_group_code(self, items):
        imports, content = Compiler.parse_template("templates/snippets/item_to_item_group.txt")
        combined_contents = ""
        for item in items:
            content_copy = content[:]

            item_space, item_var = self.get_space_and_var_of_item(item)

            content_copy = Compiler.bulk_replace(content_copy, {f"%itemSpace%": item_space, f"%itemVar%": item_var})
            combined_contents += content_copy + "\n"
        return combined_contents


compiler = Compiler("cool_minecraft_mod")
compiler.compile()
compiler.redo_gradle()
compiler.run_client()