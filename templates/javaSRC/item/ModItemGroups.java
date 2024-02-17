package %domain%.item;

%imports%

import %domain%.ModMain;

public class ModItemGroups {
    %insertItemGroups%

    public static void registerItemGroups() {
        ModMain.LOGGER.info("Registering Item Groups");
    }
}
