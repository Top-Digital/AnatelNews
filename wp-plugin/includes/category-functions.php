<?php
// Função para contar os posts da categoria selecionada
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

// Função para garantir que a categoria Anatel News exista
function anatelnews_ensure_category_exists() {
    $category_name = 'Anatel News';
    $category_slug = 'anatel-news';
    $category_id = get_option('anatelnews_category');

    if (!$category_id || !term_exists($category_id, 'category')) {
        $existing_category = get_category_by_slug($category_slug);
        if ($existing_category) {
            $category_id = $existing_category->term_id;
        } else {
            $category_id = wp_insert_category(array(
                'cat_name' => $category_name,
                'category_nicename' => $category_slug,
                'category_description' => 'Notícias da Anatel'
            ));
        }
        update_option('anatelnews_category', $category_id);
    }

    return $category_id;
}
?>
