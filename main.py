from webapp2 import WSGIApplication, Route


# Map URLs to handlers
routes = [
    Route('/', handler='handlers.RootHandler', name='root'),
    Route('/signup', handler='handlers.SignupHandler', name='signup'),
    Route('/login', handler='handlers.LoginHandler', name='login'),
    Route('/logout', handler='handlers.LogoutHandler', name='logout'),
    Route('/new', handler='handlers.NewPostHandler', name='new_post'),
    Route('/<post_id:\d+>', handler='handlers.BlogPostHandler', name='post'),
    Route('/edit/post/<post_id:\d+>', handler='handlers.EditPostHandler', name='edit_post'),
    Route('/delete/post/<post_id:\d+>', handler='handlers.DeletePostHandler', name='delete_post'),
    Route('/rate/<direction:\up|down>/<post_id:\d+>', handler='handlers.RatePostHandler', name='delete_post'),
    Route('/<post_id:\d+>/edit/comment/<comment_id:\d+>', handler='handlers.EditCommentHandler', name='edit_comment'),
    Route('/<post_id:\d+>/delete/comment/<comment_id:\d+>', handler='handlers.DeleteCommentHandler', name='delete_comment')
]

app = WSGIApplication(routes, debug=True)
