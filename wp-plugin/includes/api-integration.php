<?php
// Função para registrar endpoint customizado
function anatelnews_register_api_endpoints() {
    register_rest_route('anatelnews/v1', '/create-post', array(
        'methods' => 'POST',
        'callback' => 'anatelnews_create_post',
        'permission_callback' => '__return_true'
    ));
}
add_action('rest_api_init', 'anatelnews_register_api_endpoints');

// Função de callback para criar post
function anatelnews_create_post($data) {
    $selected_category = get_option('anatelnews_category');
    if (!$selected_category) {
        return new WP_Error('category_not_selected', 'Nenhuma categoria selecionada no plugin', array('status' => 400));
    }

    $post_data = array(
        'post_title'    => $data['title'],
        'post_content'  => $data['content'],
        'post_status'   => 'publish',
        'post_type'     => 'post',
        'post_date'     => $data['meta']['anatel_DataPublicacao'], // Use a data de publicação da Anatel
        'post_category' => array($selected_category), // Adicionar a categoria selecionada
        'meta_input'    => $data['meta'] // Inserir todos os metadados de uma vez
    );

    // Inserir o post no WordPress
    $post_id = wp_insert_post($post_data);

    if (is_wp_error($post_id)) {
        return new WP_Error('post_creation_failed', 'Failed to create post', array('status' => 500));
    }

    return new WP_REST_Response($post_data, 200);
}
?>
