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
    $post_data = array(
        'post_title'    => $data['title'],
        'post_content'  => $data['content'],
        'post_status'   => 'publish',
        'post_type'     => 'post',
        'meta_input'    => array(
            'anatel_URL' => $data['meta']['anatel_URL'],
            'anatel_Titulo' => $data['meta']['anatel_Titulo'],
            'anatel_SubTitulo' => $data['meta']['anatel_SubTitulo'],
            'anatel_ImagemChamada' => $data['meta']['anatel_ImagemChamada'],
            'anatel_Descricao' => $data['meta']['anatel_Descricao'],
            'anatel_DataPublicacao' => $data['meta']['anatel_DataPublicacao'],
            'anatel_ImagemPrincipal' => $data['meta']['anatel_ImagemPrincipal'],
            'anatel_Categoria' => $data['meta']['anatel_Categoria']
        )
    );

    // Inserir o post no WordPress
    $post_id = wp_insert_post($post_data);

    if (is_wp_error($post_id)) {
        return new WP_Error('post_creation_failed', 'Failed to create post', array('status' => 500));
    }

    return new WP_REST_Response($post_data, 200);
}
