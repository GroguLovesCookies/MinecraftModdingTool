package %domain%.datagen;


import net.fabricmc.fabric.api.datagen.v1.provider.FabricRecipeProvider;
import net.minecraft.data.server.recipe.RecipeJsonProvider;
import net.fabricmc.fabric.api.datagen.v1.FabricDataOutput;
import java.util.function.Consumer;
import %domain%.block.ModBlocks;
import %domain%.item.ModItems;
import net.minecraft.util.Identifier;
import net.minecraft.recipe.book.RecipeCategory;
import net.minecraft.item.Items;
import net.minecraft.block.Blocks;

%imports%
%importsShapeless%
%importsSmelting%


public class ModRecipeProvider extends FabricRecipeProvider {
    public ModRecipeProvider(FabricDataOutput output) {
        super(output);
    }

    @Override
    public void generate(Consumer<RecipeJsonProvider> exporter) {
        %craftingRecipes%

        %smeltingRecipes%
    }
}