package %domain%.item.custom;


import net.minecraft.item.*;
import net.minecraft.world.World;
import net.minecraft.text.Text;
import net.minecraft.client.item.TooltipContext;
import net.minecraft.util.ActionResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.entity.player.PlayerEntity;

import java.util.List;


public class %itemClass% extends Item {
    // Declare class variables here

    public %itemClass%(Settings settings%args%) {
        // Initialize class here
        super(settings);
    }

    @IfUseOnBlock@
    @Override
    public ActionResult useOnBlock(ItemUsageContext context) {
        // Triggers when used on block
        BlockPos clickedPos = context.getBlockPos();
        PlayerEntity player = context.getPlayer();

        return ActionResult.SUCCESS;
    }
    @EndIfUseOnBlock@

    @IfAppendTooltip@
    @Override
    public void appendTooltip(ItemStack itemStack, @Nullable World world, List<Text> tooltip, TooltipContext tooltipContext) {
        // Add tooltips here
        // tooltip.add(Text.translatable("TRANSLATION KEY"));
        // tooltip.add(Text.literal("TOOLTIP TEXT"));
        super.appendTooltip(itemStack, world, tooltip, tooltipContext);
    }
    @EndIfAppendTooltip@
}