<?php
/**
 * Plugin Name: Anatel News
 * Description: Plugin para integrar notícias da Anatel no WordPress.
 * Version: 1.01
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
require_once plugin_dir_path(__FILE__) . 'includes/custom_single_random_category_retrip.php';


// Adicionar hooks necessários
add_action('add_meta_boxes', 'anatelnews_add_custom_box');
add_action('save_post', 'anatelnews_save_postdata');
add_action('admin_menu', 'anatelnews_create_menu');
add_action('the_content', 'anatelnews_display_custom_fields');

// Função para contar os posts da categoria 2
function anatelnews_count_posts_by_category($category_id) {
    $args = array(
        'category' => $category_id,
        'post_type' => 'post',
        'post_status' => 'any',
        'numberposts' => -1
    );
    $posts = get_posts($args);
    return count($posts);
}

// Função para criar o menu de configurações do plugin
function anatelnews_create_menu() {
    add_menu_page(
        'Anatel News Settings (' . anatelnews_count_posts_by_category(2) . ' posts)', // Título da página
        'Anatel News', // Título do menu
        'manage_options', // Capacidade
        'anatelnews_settings', // Slug do menu
        'anatelnews_settings_page', // Função de callback
        'dashicons-admin-generic' // Ícone do menu
    );
}

// Função para renderizar a página de configurações
function anatelnews_settings_page() {
    $is_hidden = get_option('anatelnews_ocultar_posts');
    ?>
    <div class="wrap">
        <h1>Anatel News Settings (<?php echo anatelnews_count_posts_by_category(2); ?> posts)</h1>
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
                    <th scope="row"><?php echo $is_hidden ? 'Ocultar posts da Anatel' : 'Ocultar posts da Anatel'; ?></th>
                    <td><input type="checkbox" name="anatelnews_ocultar_posts" value="1" <?php checked(1, $is_hidden, true); ?> /></td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
        <form method="post" action="<?php echo admin_url('admin-post.php'); ?>" onsubmit="return confirmDeletion('Todos os posts serão deletados. Você tem certeza?');">
            <input type="hidden" name="action" value="anatelnews_delete_all_posts" />
            <input type="submit" name="anatelnews_delete_all_posts" class="button button-secondary" value="Deletar Todos os Posts"/>
        </form>
        <form method="post" action="<?php echo admin_url('admin-post.php'); ?>" onsubmit="return confirmDeletion('Todos os posts dessa categoria serão removidos. Você tem certeza?');">
            <input type="hidden" name="action" value="anatelnews_delete_posts" />
            <input type="hidden" name="anatelnews_delete_posts_nonce" value="<?php echo wp_create_nonce('anatelnews_delete_posts'); ?>" />
            <input type="submit" name="anatelnews_delete_posts" class="button button-secondary" value="Deletar Posts da Anatel"/>
        </form>
    </div>

    <!-- Modal CSS -->
    <div id="deletionModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <p id="modalMessage">Você tem certeza?</p>
            <div class="progress-bar" id="progressBar">
                <div class="progress-bar-fill" id="progressBarFill"></div>
            </div>
            <button id="confirmDelete" class="button button-primary">Confirmar</button>
            <button id="cancelDelete" class="button button-secondary">Cancelar</button>
        </div>
    </div>

    <style>
        /* Modal CSS */
        .modal {
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgb(0,0,0);
            background-color: rgba(0,0,0,0.4);
            padding-top: 60px;
        }
        .modal-content {
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 80%;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
        }
        .close:hover,
        .close:focus {
            color: black;
            text-decoration: none;
            cursor: pointer;
        }
        .progress-bar {
            width: 100%;
            background-color: #f3f3f3;
            border: 1px solid #ccc;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 20px;
        }
        .progress-bar-fill {
            height: 20px;
            width: 0%;
            background-color: #4caf50;
            text-align: center;
            line-height: 20px;
            color: white;
        }
    </style>

    <script>
        function confirmDeletion(message) {
            var modal = document.getElementById("deletionModal");
            var span = document.getElementsByClassName("close")[0];
            var confirmButton = document.getElementById("confirmDelete");
            var cancelButton = document.getElementById("cancelDelete");
            var progressBarFill = document.getElementById("progressBarFill");
            var modalMessage = document.getElementById("modalMessage");

            modalMessage.innerText = message;
            modal.style.display = "block";

            span.onclick = function() {
                modal.style.display = "none";
            }
            cancelButton.onclick = function() {
                modal.style.display = "none";
            }
            confirmButton.onclick = function() {
                var ajaxurl = "<?php echo admin_url('admin-ajax.php'); ?>";
                var totalPosts = <?php echo anatelnews_count_posts_by_category(2); ?>;
                var progress = 0;

                var interval = setInterval(function() {
                    if (progress >= 100) {
                        clearInterval(interval);
                        modal.style.display = "none";
                        location.reload();
                    } else {
                        var request = new XMLHttpRequest();
                        request.open("POST", ajaxurl, true);
                        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
                        request.onreadystatechange = function() {
                            if (request.readyState == 4 && request.status == 200) {
                                progress += (100 / totalPosts);
                                progressBarFill.style.width = progress + "%";
                            }
                        }
                        request.send("action=anatelnews_batch_delete&nonce=<?php echo wp_create_nonce('anatelnews_batch_delete'); ?>");
                    }
                }, 500);
            }

            window.onclick = function(event) {
                if (event.target == modal) {
                    modal.style.display = "none";
                }
            }

            return false;
        }
    </script>
    <?php
}

// Registrar configurações
add_action('admin_init', 'anatelnews_register_settings');
function anatelnews_register_settings() {
    register_setting('anatelnews-settings-group', 'anatelnews_webhook_token');
    register_setting('anatelnews-settings-group', 'anatelnews_ocultar_posts');
}

// Função para deletar todos os posts
add_action('admin_post_anatelnews_delete_all_posts', 'anatelnews_delete_all_posts');
function anatelnews_delete_all_posts() {
    $args = array(
        'post_type' => 'post',
        'post_status' => 'any',
        'numberposts' => -1
    );

    $posts = get_posts($args);

    foreach ($posts as $post) {
        wp_delete_post($post->ID, true);
    }

    echo 'Todos os posts foram deletados.';
    wp_die();
}

// Função para deletar posts da categoria Anatel
add_action('wp_ajax_anatelnews_batch_delete', 'anatelnews_batch_delete');
function anatelnews_batch_delete() {
    check_ajax_referer('anatelnews_batch_delete', 'nonce');

    $args = array(
        'category' => 2,
        'post_type' => 'post',
        'post_status' => 'any',
        'numberposts' => 1
    );

    $posts = get_posts($args);

    if (!empty($posts)) {
        wp_delete_post($posts[0]->ID, true);
        echo json_encode(array('success' => true));
    } else {
        echo json_encode(array('success' => false));
    }

    wp_die();
}
?>
