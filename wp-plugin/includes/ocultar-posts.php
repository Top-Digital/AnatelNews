<?php
// Função para ocultar todos os posts da categoria Anatel
function anatelnews_hide_posts_by_category() {
    $category_id = 2;
    $args = array(
        'category' => $category_id,
        'post_type' => 'post',
        'post_status' => 'publish',
        'numberposts' => -1
    );

    $posts = get_posts($args);

    foreach ($posts as $post) {
        wp_update_post(array(
            'ID' => $post->ID,
            'post_status' => 'draft'
        ));
    }

    echo 'Todos os posts da categoria foram ocultados.';
    wp_die();
}

add_action('admin_post_anatelnews_hide_posts', 'anatelnews_hide_posts_by_category');
?>
