class PhotoInCart(generics.ListCreateAPIView):
    model = CartPhoto
    serializer_class = CartPhotoSerializer
    permission_classes = (IsCartOwner, IsAuthenticated)

    def create_photo_rm_prices(self, prices, cart_photo):
        options = [int(option) for option in prices.get('selected')]
        date = prices.get('date')
        if date:
            date = get_normal_date(date)
            cart_photo.start_date = date
        else:
            raise
        rm_calc = RMCalcValidator(options)
        if rm_calc.is_valid():

            # cart_photo.valid_till = datetime(date) + timedelta
            cart_photo.price_rm.clear()
            for option in options:
                cart_photo.price_rm.add(option)
            cart_photo.save()
            return CartPhotoSerializer(cart_photo).data
        else:
            raise

    def create_photo_rf_prices(self, prices, cart_photo):
        cart_photo.price_rf.clear()
        for price in prices:
            cart_photo.price_rf.add(price)
        cart_photo.save()
        return CartPhotoSerializer(cart_photo).data

    def post(self, request, *args, **kwargs):
        try:
            with transaction.commit_on_success():
                photo = Photo.objects.get(pk=request.DATA['photo'])
                owner = User.objects.get(pk=request.DATA['owner'])

                cart_photo, created = CartPhoto.objects.get_or_create(photo=photo,
                                                                      owner=owner)
                if photo.royalty_free:
                    price_rf = request.DATA.getlist('price_rf[]')
                    result = self.create_photo_rf_prices(price_rf, cart_photo)
                elif photo.rights_managed:
                    price = dict()
                    price['selected'] = request.DATA.getlist('price_rm[options][]')
                    price['date'] = request.DATA.getlist('price_rm[date]')[0]
                    result = self.create_photo_rm_prices(price, cart_photo)

        except Exception, error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'data': result}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return CartPhoto.objects.filter(owner=self.request.user)