from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, MessageHandler, filters
from database.queries import reset_character_stats, update_character_strength, update_character_weakness, update_character_vul
from game.sanity import increase_sanity as incSanity, decrease_sanity as decSanity

# 定义会话状态
PERSONA_SELECT = 0

async def reset(update: Update, context: CallbackContext) -> None:
    reset_character_stats()
    await update.message.reply_text('角色状态已恢复。')

async def strength(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的强壮层数。格式: /strength 角色名 层数')
        return

    character_name, strength_change = args
    try:
        strength_change = int(strength_change)
    except ValueError:
        await update.message.reply_text('强壮层数必须为整数！')
        return
    
    # 获取当前状态
    from database.queries import get_character_stats
    before_stats = get_character_stats(character_name)
    if not before_stats:
        await update.message.reply_text(f'未找到角色 {character_name}')
        return
    
    # 更新强壮
    update_character_strength(character_name, strength_change)
    
    # 获取更新后状态
    after_stats = get_character_stats(character_name)
    after_strength = after_stats[4]
    after_weakness = after_stats[5]
    
    action = "增加" if strength_change > 0 else "减少"
    await update.message.reply_text(f'{character_name} 的强壮层数{action}了 {abs(strength_change)}')

async def weakness(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的虚弱层数。格式: /weakness 角色名 层数')
        return

    character_name, weakness_change = args
    try:
        weakness_change = int(weakness_change)
    except ValueError:
        await update.message.reply_text('虚弱层数必须为整数！')
        return
    
    # 获取当前状态
    from database.queries import get_character_stats
    before_stats = get_character_stats(character_name)
    if not before_stats:
        await update.message.reply_text(f'未找到角色 {character_name}')
        return
    
    # 更新虚弱
    update_character_weakness(character_name, weakness_change)
    
    # 获取更新后状态
    after_stats = get_character_stats(character_name)
    after_strength = after_stats[4]
    after_weakness = after_stats[5]
    
    action = "增加" if weakness_change > 0 else "减少"
    await update.message.reply_text(f'{character_name} 的虚弱层数{action}了 {abs(weakness_change)}')

async def sanity(update: Update, context: CallbackContext) -> None:
    """
    调整角色的理智值。格式: /sanity 角色名 数值
    数值正数表示增加，负数表示减少。
    """
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和调整的理智值。格式: /sanity 角色名 数值（正为增加、负为减少）')
        return

    character_name, sanity_change = args
    try:
        sanity_change = int(sanity_change)
    except ValueError:
        await update.message.reply_text('理智值必须为整数！')
        return

    if sanity_change >= 0:
        new_sanity = incSanity(character_name, sanity_change)
        action = "增加"
    else:
        new_sanity = decSanity(character_name, -sanity_change)
        action = "减少"

    await update.message.reply_text(f'{character_name} 的理智值{action}了 {abs(sanity_change)} 点，现在的理智值是 {new_sanity}。')

async def vul(update: Update, context: CallbackContext) -> None:
    """
    调整角色的易伤/守护值。格式: /vul 角色名 数值
    正值表示增加易伤，负值表示增加守护，两者抵消。
    """
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('请提供角色名称和修改的易伤/守护值。格式: /vul 角色名 值（正值表示增加易伤，负值表示增加守护）')
        return

    character_name, vul_change = args
    try:
        vul_change = int(vul_change)
    except ValueError:
        await update.message.reply_text('易伤/守护值必须为整数！')
        return
    
    # 获取当前状态
    from database.queries import get_character_stats
    before_stats = get_character_stats(character_name)
    if not before_stats:
        await update.message.reply_text(f'未找到角色 {character_name}')
        return
    
    # 更新易伤/守护
    update_character_vul(character_name, vul_change)
    
    # 获取更新后状态
    after_stats = get_character_stats(character_name)
    after_vul = after_stats[7]  # vul 是角色信息中的第 8 列
    
    if vul_change > 0:
        action = "增加了易伤"
    elif vul_change < 0:
        action = "增加了守护"
    
    status = "易伤" if after_vul > 0 else "守护" if after_vul < 0 else "无状态"
    value = abs(after_vul) if after_vul != 0 else 0
    
    await update.message.reply_text(f'{character_name} {action} {abs(vul_change)}')

async def panel(update: Update, context: CallbackContext) -> None:
    """
    显示五个主要角色（珏、露、笙、莹、曦）的面板信息，
    角色名有个性化图标装饰。
    使用方式: /panel
    """
    from database.queries import get_character_panels
    from game.stagger import get_stagger_description  # 导入混乱状态描述函数
    
    panels = get_character_panels()
    
    if not panels:
        await update.message.reply_text('未找到角色信息。')
        return
    
    message = "【角色面板信息】\n\n"
    
    for _, panel in panels.items():
        message += f" {panel['name']} \n"  # 使用带图标的名称
        
        # 添加覆写人格信息
        if panel.get('persona'):
            message += f"【人格：{panel['persona']}】\n"
        
        # 显示混乱状态
        if panel.get('is_stagger', 0) > 0:
            stagger_desc = get_stagger_description(panel['is_stagger'])
            message += f"{stagger_desc}\n"
        
        # 显示战斗状态
        if not panel['can_fight']:
            message += "【无法战斗】\n"
            
        message += f"体力：{panel['health']}\n"
        message += f"理智：{panel['sanity']}\n"
        
        if 'strength' in panel:
            message += f"强壮：{panel['strength']}\n"
        if 'weakness' in panel:
            message += f"虚弱：{panel['weakness']}\n"
        if 'vulnerability' in panel:
            message += f"易伤：{panel['vulnerability']}\n"
        if 'protection' in panel:
            message += f"守护：{panel['protection']}\n"
        
        message += "\n"
    
    await update.message.reply_text(message)

async def persona_start(update: Update, context: CallbackContext) -> int:
    """启动人格覆写流程"""
    args = context.args
    if not args:
        await update.message.reply_text("请提供角色名称。格式：/persona 角色名")
        return ConversationHandler.END
    
    character_name = args[0]
    # 保存角色名以便后续使用
    context.user_data['persona_character'] = character_name
    
    # 从数据库获取可用人格
    from database.queries import get_available_personas
    personas = get_available_personas(character_name)
    
    if not personas:
        await update.message.reply_text(f"未找到 {character_name} 可用的人格配置。")
        return ConversationHandler.END
    
    # 显示人格列表
    message = f"【{character_name} 的可用人格】\n\n"
    message += "0. 初始人格\n"
    
    for i, persona in enumerate(personas, 1):
        persona_id, name, health, max_health, dlv = persona
        message += f"{i}. {name} (体力: {health}/{max_health}, DLV: {dlv})\n"
    
    # 保存人格ID列表以便后续查找
    context.user_data['persona_list'] = [p[0] for p in personas]
    
    message += "\n请输入数字选择要覆写的人格："
    await update.message.reply_text(message)
    return PERSONA_SELECT

async def persona_select(update: Update, context: CallbackContext) -> int:
    """处理用户选择的人格"""
    character_name = context.user_data.get('persona_character')
    persona_list = context.user_data.get('persona_list', [])
    
    try:
        choice = int(update.message.text.strip())
        
        # 处理选择
        if choice == 0:  # 恢复默认状态
            from database.queries import reset_character_to_default
            reset_character_to_default(character_name)
            await update.message.reply_text(f"{character_name} 已恢复为初始人格。")
        elif 1 <= choice <= len(persona_list):  # 切换到选择的人格
            from database.queries import set_character_persona
            persona_id = persona_list[choice - 1]
            persona_name = set_character_persona(character_name, persona_id)
            
            if persona_name:
                await update.message.reply_text(f"{character_name} 已覆写 {persona_name} 的人格。")
            else:
                await update.message.reply_text("人格覆写失败。")
        else:  # 无效的选择
            await update.message.reply_text("无效的选择。请输入列表中显示的数字。")
            return PERSONA_SELECT
            
    except ValueError:
        await update.message.reply_text("请输入有效的数字。")
        return PERSONA_SELECT
        
    # 清理会话数据
    if 'persona_character' in context.user_data:
        del context.user_data['persona_character']
    if 'persona_list' in context.user_data:
        del context.user_data['persona_list']
        
    return ConversationHandler.END

async def persona_cancel(update: Update, context: CallbackContext) -> int:
    """取消人格切换操作"""
    await update.message.reply_text("人格覆写已取消。")
    
    # 清理会话数据
    if 'persona_character' in context.user_data:
        del context.user_data['persona_character']
    if 'persona_list' in context.user_data:
        del context.user_data['persona_list']
        
    return ConversationHandler.END

def get_reset_handler():
    return CommandHandler("reset", reset)

def get_strength_handler():
    return CommandHandler("strength", strength)

def get_weakness_handler():
    return CommandHandler("weakness", weakness)

def get_sanity_handler():
    return CommandHandler("sanity", sanity)

def get_vul_handler():
    return CommandHandler("vul", vul)

def get_panel_handler():
    return CommandHandler("panel", panel)

def get_persona_handler():
    """返回人格覆写命令的处理器"""
    return ConversationHandler(
        entry_points=[CommandHandler("persona", persona_start)],
        states={
            PERSONA_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, persona_select)],
        },
        fallbacks=[CommandHandler("cancel", persona_cancel)]
    )

def get_character_management_handlers():
    """
    返回一个列表，包含各种角色管理指令处理器
    """
    return [
        get_reset_handler(), 
        get_strength_handler(), 
        get_weakness_handler(), 
        get_sanity_handler(),
        get_vul_handler(),
        get_panel_handler(),
        get_persona_handler()  # 新增人格覆写处理器
    ]