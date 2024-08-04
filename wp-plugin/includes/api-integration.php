<?php
function anatelnews_fetch_posts() {
    $webhook_token = get_option('anatelnews_webhook_token');
    $api_url = 'http://localhost:5000/getnewposts';

    $response = wp_remote_get($api_url, array(
        'headers' => array(
            'Authorization' => 'Bearer ' . $webhook_token
        )
    ));

    if (is_wp_error($response)) {
        return;
    }

    $posts = json_decode(wp_remote_retrieve_body($response), true);

    foreach ($posts as $post) {
        if ($post['action'] === 'delete') {
            // Lógica para deletar o post
        } elseif ($post['action'] === 'update') {
            // Lógica para atualizar o post
        } else {
            // Lógica para criar o post
        }
    }
}
add_action('init', 'anatelnews_fetch_posts');
?>
