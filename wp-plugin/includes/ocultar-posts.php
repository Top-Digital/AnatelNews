<?php
// Função para deletar todos os posts de uma categoria específica
function anatelnews_delete_posts_by_category($category_id) {
    $args = array(
        'category' => $category_id,
        'post_type' => 'post',
        'post_status' => 'any',
        'numberposts' => -1
    );

    $posts = get_posts($args);

    foreach ($posts as $post) {
        wp_delete_post($post->ID, true);
    }
}

// Hook para deletar posts ao inicializar o WordPress
add_action('init', function() {
    if (is_admin() && current_user_can('manage_options')) {
        anatelnews_delete_posts_by_category(2);
    }
});
