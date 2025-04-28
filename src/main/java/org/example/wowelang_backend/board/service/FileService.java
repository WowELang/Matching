package org.example.wowelang_backend.board.service;

import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import lombok.RequiredArgsConstructor;
import net.coobird.thumbnailator.Thumbnails;
import org.example.wowelang_backend.board.domain.Image;
import org.example.wowelang_backend.board.dto.PostImageResponseDTO;
import org.example.wowelang_backend.board.repository.ImageRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class FileService {

    private final AmazonS3 amazonS3;
    private final ImageRepository imageRepository;

    @Value("${cloud.aws.s3.bucket}")
    private String bucket;

    @Transactional
    public PostImageResponseDTO uploadCompressedImage(InputStream inputStream, String filename, String contentType) throws IOException {
        try {
            ByteArrayOutputStream compressedOut = new ByteArrayOutputStream();

            Thumbnails.of(inputStream)
                    .size(1024, 1024)
                    .outputQuality(1.0)
                    .outputFormat("jpg")
                    .toOutputStream(compressedOut);

            byte[] compressedImage = compressedOut.toByteArray();
            InputStream compressedInputStream = new ByteArrayInputStream(compressedImage);

            String extension = ".jpg";
            String uuid = UUID.randomUUID().toString();
            String key = "post-images/" + uuid + "_" + filename + extension;

            ObjectMetadata metadata = new ObjectMetadata();
            metadata.setContentType(contentType);
            metadata.setContentLength(compressedImage.length);

            try {
                amazonS3.putObject(new PutObjectRequest(bucket, key, compressedInputStream, metadata));
            } catch (Exception e) {
                throw new RuntimeException("S3 업로드 중 에러 발생");
            }

            String url = amazonS3.getUrl(bucket, key).toString();

            imageRepository.save(Image.builder()
                    .imageKey(key)
                    .imageUrl(url)
                    .isPosted(false)
                    .build());

            return new PostImageResponseDTO(key, url);
        } catch (Exception e) {
            throw new RuntimeException("이미지 업로드 중 에러 발생");
        }
    }
}
