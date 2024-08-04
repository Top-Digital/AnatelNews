<?php
/**
 * Plugin Name: Anatel News
 * Description: Plugin para integrar notícias da Anatel no WordPress.
 * Version: 1.02
 * Author: Adriano Alves Dal Cin Costa
 */

// Proteger contra acesso direto
if (!defined('ABSPATH')) {
    exit;
}

// Incluir arquivos necessários
require_once plugin_dir_path(__FILE__) . 'includes/custom-fields.php';
require_once plugin_dir_path(__FILE__) . 'includes/api-integration.php';
require_once plugin_dir_path(__FILE__) . 'includes/register-fields.php';
require_once plugin_dir_path(__FILE__) . 'includes/display-fields.php';
require_once plugin_dir_path(__FILE__) . 'includes/ocultar-posts.php';

// Adicionar hooks necessários
add_action('add_meta_boxes', 'anatelnews_add_custom_box');
add_action('save_post', 'anatelnews_save_postdata');
add_action('admin_menu', 'anatelnews_create_menu');
add_action('the_content', 'anatelnews_display_custom_fields');

// Função para criar o menu de configurações do plugin
function anatelnews_create_menu() {
    $selected_category = get_option('anatelnews_category');
    $count = $selected_category ? anatelnews_count_posts_by_category($selected_category) : 0;
    add_menu_page(
        'Anatel News Settings (' . $count . ' posts)', // Título da página
        'Anatel News', // Título do menu
        'manage_options', // Capacidade
        'anatelnews_settings', // Slug do menu
        'anatelnews_settings_page', // Função de callback
        'dashicons-admin-generic' // Ícone do menu
    );
}

// Função para renderizar a página de configurações
function anatelnews_settings_page() {
    $categories = get_categories(
        array(
            'hide_empty' => false
        )
    );
    $selected_category = get_option('anatelnews_category');
    $is_hidden = get_option('anatelnews_ocultar_posts');
    ?>
    <div class="wrap">
        <h1>Anatel News Settings</h1>
        <form method="post" action="options.php">
            <?php
            settings_fields('anatelnews-settings-group');
            do_settings_sections('anatelnews-settings-group');
            ?>
            <table class="form-table">
                <tr valign="top">
                    <th scope="row">Webhook Token</th>
                    <td><input type="text" name="anatelnews_webhook_token" value="<?php echo esc_attr(get_option('anatelnews_webhook_token')); ?>" /></td>
                </tr>
                <tr valign="top">
                    <th scope="row">Selecionar Categoria</th>
                    <td>
                        <select name="anatelnews_category">
                            <option value="">Selecione uma categoria</option>
                            <?php foreach ($categories as $category) : ?>
                                <option value="<?php echo $category->term_id; ?>" <?php selected($selected_category, $category->term_id); ?>>
                                    <?php echo $category->name; ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </td>
                </tr>
                <tr valign="top">
                    <th scope="row"><?php echo $is_hidden ? 'Ocultar posts da Anatel' : 'Ocultar posts da Anatel'; ?></th>
                    <td><input type="checkbox" name="anatelnews_ocultar_posts" value="1" <?php checked(1, $is_hidden, true); ?> /></td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

// Registrar configurações
add_action('admin_init', 'anatelnews_register_settings');
function anatelnews_register_settings() {
    register_setting('anatelnews-settings-group', 'anatelnews_webhook_token');
    register_setting('anatelnews-settings-group', 'anatelnews_category');
    register_setting('anatelnews-settings-group', 'anatelnews_ocultar_posts');
}
