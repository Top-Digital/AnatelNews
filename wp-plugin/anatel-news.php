<?php
/*
Plugin Name: Anatel News
Description: Fetch news from MongoDB and display in WordPress.
Version: 1.0
Author: Your Name
*/

// Adiciona a rota REST API para receber dados do MongoDB
add_action('rest_api_init', function () {
    register_rest_route('anatel-news/v1', '/webhook', array(
        'methods' => 'POST',
        'callback' => 'anatel_news_webhook_callback',
    ));
});

// Callback para processar os dados recebidos
function anatel_news_webhook_callback($request) {
    $params = $request->get_json_params();
    $token = $request->get_header('X-Webhook-Token');

    // Obtém o token de segurança da configuração do WordPress
    $env_token = get_option('anatel_news_webhook_token');

    // Verifica o token de segurança
    if ($token !== $env_token) {
        return new WP_REST_Response('Unauthorized', 401);
    }

    // Campos obrigatórios
    $required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_DataPublicacao', 'anatel_TextMateria'];

    // Verifica se todos os campos obrigatórios estão preenchidos
    foreach ($required_fields como $field) {
        if (empty($params[$field])) {
            return new WP_REST_Response('Missing required field: ' . $field, 400);
        }
    }

    if ($params) {
        // Adiciona a atribuição ao conteúdo da matéria
        $attribution = '<div class="texto-copyright">
            Todo o conteúdo deste site está publicado sob a licença <a rel="license" href="https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR">Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada</a>.
            Fonte: <a href="' . esc_url($params['anatel_URL']) . '" target="_blank">Anatel</a>.
        </div>';
        $params['anatel_TextMateria'] .= $attribution;

        // Verifica se o post já existe
        $existing_post_id = get_post_by_mongo_id($params['wordpressPostId']);

        // Define a categoria
        $category_id = 307; // ID da categoria "Notícias Anatel - NewsLetter"

        if ($existing_post_id) {
            // Atualiza o post existente se a data de atualização for diferente
            $existing_post = get_post($existing_post_id);
            if ($existing_post && get_post_meta($existing_post_id, 'mongo_update_date', true) !== $params['anatel_DataAtualizacao']) {
                wp_update_post(array(
                    'ID' => $existing_post_id,
                    'post_title' => wp_strip_all_tags($params['anatel_Titulo']),
                    'post_content' => $params['anatel_TextMateria'],
                    'post_category' => array($category_id)
                ));
                update_post_meta($existing_post_id, 'mongo_update_date', $params['anatel_DataAtualizacao']);
                return new WP_REST_Response('Post updated', 200);
            } else {
                return new WP_REST_Response('No update needed', 200);
            }
        } else {
            // Cria um novo post
            $post_id = wp_insert_post(array(
                'post_title' => wp_strip_all_tags($params['anatel_Titulo']),
                'post_content' => $params['anatel_TextMateria'],
                'post_status' => 'publish',
                'post_type' => 'post',
                'post_category' => array($category_id)
            ));

            if ($post_id) {
                add_post_meta($post_id, 'mongo_id', $params['wordpressPostId']);
                add_post_meta($post_id, 'mongo_update_date', $params['anatel_DataAtualizacao']);
                return new WP_REST_Response('Post created', 200);
            } else {
                return new WP_REST_Response('Failed to insert post', 500);
            }
        }
    }
    return new WP_REST_Response('Invalid request', 400);
}

// Função para obter um post pelo ID do MongoDB
function get_post_by_mongo_id($mongo_id) {
    global $wpdb;
    $meta_key = 'mongo_id';
    $query = $wpdb->prepare("SELECT post_id FROM $wpdb->postmeta WHERE meta_key = %s AND meta_value = %s", $meta_key, $mongo_id);
    $post_id = $wpdb->get_var($query);
    return $post_id ? intval($post_id) : false;
}

// Adiciona uma página de configuração para o plugin
add_action('admin_menu', function () {
    add_options_page('Anatel News Settings', 'Anatel News', 'manage_options', 'anatel-news', 'anatel_news_settings_page');
});

// Renderiza a página de configurações do plugin
function anatel_news_settings_page() {
    if (isset($_POST['anatel_news_webhook_token'])) {
        update_option('anatel_news_webhook_token', sanitize_text_field($_POST['anatel_news_webhook_token']));
        echo '<div class="updated"><p>Token de webhook atualizado com sucesso!</p></div>';
    }
    $token = get_option('anatel_news_webhook_token');
    ?>
    <div class="wrap">
        <h1>Configurações do Anatel News</h1>
        <form method="post">
            <label for="anatel_news_webhook_token">Token de Webhook</label>
            <input type="text" id="anatel_news_webhook_token" name="anatel_news_webhook_token" value="<?php echo esc_attr($token); ?>" class="regular-text" />
            <?php submit_button('Salvar Configurações'); ?>
        </form>
    </div>
    <?php
}
?>
