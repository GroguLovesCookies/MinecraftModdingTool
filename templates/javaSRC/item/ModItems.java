package %domain%.item;

import %domain%.ModMain;
import net.minecraft.item.*;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;

%imports%

public class ModItems {
    %registerItems%


    private static Item registerItem(String name, Item item) {
        return Registry.register(Registries.ITEM, new Identifier(ModMain.MOD_ID, name), item);
    }

    public static void registerModItems() {
        ModMain.LOGGER.info("Registering Items");
    }
}
