<?php
/**
 * Plugin Name: Anatel News
 * Description: Plugin para integrar notícias da Anatel no WordPress.
 * Version: 1.0
 * Author: Adriano Alves Dal Cin Costa
 */

// Proteger contra acesso direto
if (!defined('ABSPATH')) {
    exit;
}

// Incluir arquivos necessários
require_once plugin_dir_path(__FILE__) . 'includes/custom-fields.php';
require_once plugin_dir_path(__FILE__) . 'includes/api-integration.php';
require_once plugin_dir_path(__FILE__) . 'includes/display-fields.php';
require_once plugin_dir_path(__FILE__) . 'includes/ocultar-posts.php';

// Adicionar hooks necessários
add_action('add_meta_boxes', 'anatelnews_add_custom_box');
add_action('save_post', 'anatelnews_save_postdata');
add_action('admin_menu', 'anatelnews_create_menu');
add_action('the_content', 'anatelnews_display_custom_fields');
add_action('init', 'anatelnews_delete_posts_by_category');

// Função para criar o menu de configurações do plugin
function anatelnews_create_menu() {
    add_menu_page(
        'Anatel News Settings', // Título da página
        'Anatel News', // Título do menu
        'manage_options', // Capacidade
        'anatelnews_settings', // Slug do menu
        'anatelnews_settings_page', // Função de callback
        'dashicons-admin-generic' // Ícone do menu
    );
}

// Função para renderizar a página de configurações
function anatelnews_settings_page() {
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
}
