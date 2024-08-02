<?php
/*
Plugin Name: Custom Single Random Category Retrip
Description: Sobrescreve a função hodil_single_random_category_retrip para evitar erros após atualizações do tema.
*/

add_action('after_setup_theme', 'override_hodil_single_random_category_retrip', 100);

function override_hodil_single_random_category_retrip() {
    if (function_exists('hodil_single_random_category_retrip')) {
        remove_action('init', 'hodil_single_random_category_retrip'); // Remover se estiver adicionado em algum hook
    }

    // Redefine a função
    if (!function_exists('hodil_single_random_category_retrip')) {
        function hodil_single_random_category_retrip() {
            if ('post' === get_post_type()) {
                $category = get_the_category();
                $cat_count = count($category);

                // Verificar se $cat_count é maior que zero
                if ($cat_count > 0) {
                    $single_cat = $category[random_int(0, $cat_count - 1)];
                    if (get_the_category()) {
                        echo '<div class="single__random__category"><a href="' . esc_url(get_category_link($single_cat->term_id)) . '">' . esc_html($single_cat->cat_name) . '</a></div>';
                    }
                }
            }
        }
    }
}
