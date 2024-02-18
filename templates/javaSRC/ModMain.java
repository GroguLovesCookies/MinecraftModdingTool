package %domain%;

import net.fabricmc.api.ModInitializer;
import %domain%.item.ModItems;
import %domain%.item.ModItemGroups;
import %domain%.block.ModBlocks;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ModMain implements ModInitializer {
	public static final String MOD_ID = "%modID%";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {
		ModItems.registerModItems();
		ModItemGroups.registerItemGroups();
		ModBlocks.registerModBlocks();
	}
}